.zshrc -> 

export HF_API_KEY="API_KEY"
navi() {
    if (( $# > 0 )); then
        case "$1" in
            -h|--help)
                (cd path/navi && source venv/bin/activate && python3 navi/main.py --help)
                return
                ;;
        esac
        local tmp
        tmp=$(mktemp) || { echo "mktemp failed"; return 1; }
        (
            export NAVI_OUT="$tmp"
            cd path/navi || exit 1
            source venv/bin/activate
            python3 navi/main.py --ask "$*"
        )
        if [ -s "$tmp" ]; then
            local cmd
            cmd=$(<"$tmp")
            cmd="${cmd%$'\n'}"
            [ -n "$cmd" ] && print -z -- "$cmd"
        fi
        rm -f "$tmp"
        return
    fi
    local tmp
    tmp=$(mktemp) || { echo "mktemp failed"; return 1; }
    (
        export NAVI_OUT="$tmp"
        cd path/navi || exit 1
        source venv/bin/activate
        python3 navi/main.py
    )
    if [ -s "$tmp" ]; then
        local cmd
        cmd=$(<"$tmp")
        cmd="${cmd%$'\n'}"
        [ -n "$cmd" ] && print -z -- "$cmd"
    fi
    rm -f "$tmp"
}
