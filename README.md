# navi — Interactive CLI + AI helper

navi is a command-line tool that:
- opens an interactive command prompt with autocomplete and AI suggestions
- or answers a direct question and lets you pick a suggested command

The selected command is pushed into your Zsh input buffer (not executed automatically).

## Requirements
- Linux + Zsh
- Python 3.12+
- Virtual environment (venv)
- Packages: prompt_toolkit, InquirerPy, openai

## Installation
```bash
cd /home/oskari/Desktop/pyt/navi
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install prompt_toolkit InquirerPy openai
```

### Environment
Create a .env in the project root:
```env
HF_API_KEY=hf_xxx
```

## Zsh integration
Add this function to your ~/.zshrc (adjust paths if needed). It supports:
- navi                → interactive mode (returns selected command to the prompt)
- navi "your question" or navi --ask "your question" → ask AI and choose a command
- navi -h / --help    → show help

```zsh
# Load .env
export $(grep -v '^#' path_to/.env | xargs 2>/dev/null)

navi() {
    if (( $# > 0 )); then
        case "$1" in
            -h|--help)
                (cd path_to/navi && source venv/bin/activate && python3 navi/main.py --help)
                return
                ;;
        esac

        # Ask mode: write selected command to a temp file, then push to Zsh buffer
        local tmp
        tmp=$(mktemp) || { echo "mktemp failed"; return 1; }
        (
            export NAVI_OUT="$tmp"
            cd path_to/navi || exit 1
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

    # Interactive mode: write selected command to a temp file, then push to Zsh buffer
    local tmp
    tmp=$(mktemp) || { echo "mktemp failed"; return 1; }
    (
        export NAVI_OUT="$tmp"
        cd path_to/navi || exit 1
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
```

Reload Zsh:
```bash
source ~/.zshrc
```

## Usage
- Interactive mode:
```bash
navi
# type, see suggestions, press Enter - command appears in the prompt (not executed)
```

- Ask AI directly:
```bash
navi "how to list docker containers?"
# pick one of the suggested commands - appears in the prompt
```

- Help:
```bash
navi --help
```

## How it works
- UI: prompt_toolkit (autocomplete, bottom toolbar)
- AI suggestions: debounced input → fetch → update completer dynamically
- Zsh bridge: temp file via NAVI_OUT
  - Python writes the selected command into NAVI_OUT
  - Zsh reads it and pushes into the line editor


## Development
```bash
# run in venv
cd /home/oskari/Desktop/pyt/navi
source venv/bin/activate
python3 navi/main.py
```
