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
    if [ $# -gt 2 ]; then
        echo "usage: get_param table [where_query]"
        exit
    fi

    table=$1

    if [ $# -eq 1 ]; then
        where_query=""
    else
        where_query="WHERE $2"
    fi

    query "SELECT rowid, * FROM ${table}_parameters ${where_query}"
}

get_output(){
    if [ $# -gt 2 ]; then
        echo "usage: get_output table [where_query]"
        exit
    fi

    table=$1

    if [ $# -eq 1 ]; then
        where_query=""
    else
        where_query="WHERE $2"
    fi

    query "SELECT rowid, * FROM ${table}_output ${where_query}"
}
