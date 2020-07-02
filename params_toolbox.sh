# Set of bash functions to query parameters database

set -o noglob  # Avoid * expansion in SQL queries

query(){
    \sqlite3 parameters.db "$1"
}

select_field(){
    echo "$1" | cut -d '|' -f "$2"
}

select_column() {
    if [ $# -ne 1 ]; then
        echo "usage: select_column column_number"
        exit
    fi

    while read data; do
        select_field "$data" $1
    done
}

column() {
    if [ $# -gt 2 ]; then
        echo "usage: column table column_name"
        exit
    fi

    table=$1
    col_name=$2
    query "PRAGMA table_info($table)" \
        | grep "$col_name" \
        | select_column 1
}

get_param(){
    if [ $# -gt 3 ]; then
        echo "usage: get_param table parameter [where_query]"
        exit
    fi

    table=$1
    parameter=$2

    if [ $# -eq 2 ]; then
        where_query=""
    else
        where_query="WHERE $3"
    fi

    query "SELECT ${parameter} FROM ${table}_parameters ${where_query}"
}

get_output(){
    if [ $# -gt 3 ]; then
        echo "usage: get_output table column [where_query]"
        exit
    fi

    table=$1
    column=$2

    if [ $# -eq 2 ]; then
        where_query=""
    else
        where_query="WHERE $3"
    fi

    query "SELECT ${column} FROM ${table}_output ${where_query}"
}
