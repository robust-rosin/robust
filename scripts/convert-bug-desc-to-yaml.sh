#!/bin/bash
# https://stackoverflow.com/questions/1527049/join-elements-of-an-array
function join_by { local d=$1; shift; echo -n "$1"; shift; printf "%s" "${@/#/$d}"; }

function arr_to_yml {
  input="$1"
  elements=()
  i=0
  while IFS='|' read -ra ADDR; do
    for elem in "${ADDR[@]}"; do
      elem="$(echo "$elem" | xargs)"
      elements[$i]="'$elem'"
      ((i++))
    done
  done <<< "$input"
  yml="$(join_by ', ' "${elements[@]}")"
  yml="[${yml}]"
  echo "${yml}"
}

function fix_array {
  file="${1}"
  name="${2}"
  contents=$(grep -E "^${name}:" "${file}" | cut -d ':' -f2-)
  contents=$(echo "${contents}" | xargs)
  echo "${name}: ${contents}"

  if (echo "${contents}" | grep -q -E "\["); then
    return 0
  fi

  if [[ "${contents}" == "" ]]; then
    yml="[]";
  else
    yml="$(arr_to_yml "$contents")"
  fi

  sed -i "s#^${name}: .*\$#${name}: ${yml}#" "${file}"
}

function tidy {
  file=$1
  if ! (grep -q "YAML 1.1" "${file}"); then
    sed -i '1s#^#%YAML 1.1\n---\n#' "${file}"
  fi
  sed -i '/^\s*$/d' "${file}"
  sed -i 's#^description:$#description: >#' "${file}"

  # find keywords
  fix_array "${file}" "keywords"
  fix_array "${file}" "links"
  fix_array "${file}" "  license"
  fix_array "${file}" "  fix-in"
  # fix_array "${file}" "  languages"
}

tidy "$1"
