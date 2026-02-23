# nvim quick reference

## modes

| key | action |
|-----|--------|
| `i` | insert mode |
| `Esc` / `jk` / `kj` | back to normal mode |
| `v` | visual mode (select) |
| `V` | visual line mode |
| `;` | command mode (replaces `:`) |

## navigation

| key | action |
|-----|--------|
| `h j k l` | left / down / up / right |
| `w` / `b` | next / prev word |
| `0` / `$` | start / end of line |
| `gg` / `G` | top / bottom of file |
| `Ctrl+d` / `Ctrl+u` | half page down / up (centered) |
| `{` / `}` | jump between blank lines |
| `%` | jump to matching bracket |

## editing

| key | action |
|-----|--------|
| `dd` | delete line |
| `yy` | copy line |
| `p` | paste below |
| `u` | undo |
| `Ctrl+r` | redo |
| `d$` / `D` | delete to end of line |
| `de` | delete to end of word |
| `ci"` | change inside quotes |
| `ci(` | change inside parens |
| `gcc` | toggle comment on line |
| `gc` (visual) | toggle comment on selection |
| `J` (visual) | move selected lines down |
| `K` (visual) | move selected lines up |

## search

| key | action |
|-----|--------|
| `/pattern` | search forward |
| `?pattern` | search backward |
| `n` / `N` | next / prev match (centered) |
| `F9` | clear search highlight |
| `*` | search word under cursor |

## splits / windows

| key | action |
|-----|--------|
| `:sp` | horizontal split |
| `:vsp` | vertical split |
| `Ctrl+h/j/k/l` | move between splits |
| `Ctrl+arrows` | resize splits |

## telescope (fuzzy finder) — leader is Space

| key | action |
|-----|--------|
| `Space ff` | find files |
| `Space fg` | grep across all files |
| `Space fb` | switch buffers |
| `Space fr` | recent files |
| `Space fh` | help tags |

inside telescope: `Ctrl+j/k` to move, `Enter` to open, `Esc` to close

## file tree

| key | action |
|-----|--------|
| `Space e` | toggle file tree |

inside tree: `Enter` to open, `a` to create, `d` to delete, `r` to rename

## LSP (language features — works in Python, JS, bash, lua)

| key | action |
|-----|--------|
| `gd` | go to definition |
| `K` | show docs / type info |
| `Space rn` | rename symbol everywhere |
| `Space ca` | code actions (auto-import, fixes) |
| `[d` / `]d` | prev / next diagnostic |

## lazy.nvim (plugin manager)

| command | action |
|---------|--------|
| `:Lazy` | open plugin manager UI |
| `:Lazy sync` | update all plugins |
| `:Mason` | open LSP server manager |

## misc

| key | action |
|-----|--------|
| `Ctrl+d` (insert) | autocomplete next item |
| `Tab` (insert) | cycle through completions |
| `Enter` (insert) | confirm completion |
| `za` | toggle fold |
| `:w` | save |
| `:q` | quit |
| `:wq` | save and quit |
| `:q!` | quit without saving |
