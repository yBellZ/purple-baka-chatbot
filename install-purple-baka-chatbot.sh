#!/usr/bin/env bash
#
# install-purple-baka-chatbot.sh
#
# Instala e habilita o serviço systemd que executa:
#   uv run <diretório do projeto>/chatbot/send_message.py
#
# O diretório do projeto é resolvido automaticamente como a pasta onde
# este script está localizado (não depende de caminho fixo no $HOME).
# Coloque este script na raiz do repositório, ao lado da pasta "chatbot/".
#
# Uso:
#   ./install-purple-baka-chatbot.sh
#
# Pode ser rodado como usuário normal (com sudo disponível) ou já com sudo.

set -euo pipefail

# --- Configurações (ajuste se necessário) -----------------------------------
SERVICE_NAME="purple-baka-chatbot"
SCRIPT_REL_PATH="chatbot/send_message.py"
SERVICE_TYPE="oneshot"   # troque para "simple" se o script ficar rodando em loop

# --- Descobre o diretório do projeto a partir da localização deste script --
# Assume que este install script está na raiz do projeto
# (mesmo nível de "chatbot/"). Ajuste PROJECT_DIR manualmente se não for o caso.
SOURCE="${BASH_SOURCE[0]}"
while [[ -h "$SOURCE" ]]; do
    DIR=$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)
    SOURCE=$(readlink "$SOURCE")
    [[ "$SOURCE" != /* ]] && SOURCE="$DIR/$SOURCE"
done
PROJECT_DIR=$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)
SCRIPT_PATH="$PROJECT_DIR/$SCRIPT_REL_PATH"

# --- Descobre o usuário e o home reais (mesmo se rodado com sudo) -----------
if [[ -n "${SUDO_USER:-}" ]]; then
    RUN_USER="$SUDO_USER"
else
    RUN_USER="$(whoami)"
fi

USER_HOME=$(getent passwd "$RUN_USER" | cut -d: -f6)

if [[ -z "$USER_HOME" ]]; then
    echo "Erro: não consegui descobrir o home de '$RUN_USER'." >&2
    exit 1
fi

echo "Usuário alvo   : $RUN_USER"
echo "Home           : $USER_HOME"
echo "Diretório proj.: $PROJECT_DIR"
echo "Script         : $SCRIPT_PATH"
echo

# --- Valida se o script existe ----------------------------------------------
if [[ ! -f "$SCRIPT_PATH" ]]; then
    echo "Aviso: não encontrei '$SCRIPT_PATH'." >&2
    echo "Confira se o repositório já foi clonado nesse caminho antes de continuar." >&2
    read -rp "Continuar mesmo assim? [y/N] " resp
    [[ "$resp" =~ ^[Yy]$ ]] || exit 1
fi

# --- Descobre o binário do uv -----------------------------------------------
UV_BIN=""
for candidate in "$USER_HOME/.local/bin/uv" "$USER_HOME/.cargo/bin/uv" "/usr/local/bin/uv" "/usr/bin/uv"; do
    if [[ -x "$candidate" ]]; then
        UV_BIN="$candidate"
        break
    fi
done

if [[ -z "$UV_BIN" ]]; then
    UV_BIN=$(command -v uv || true)
fi

if [[ -z "$UV_BIN" ]]; then
    echo "Erro: não encontrei o binário 'uv'. Instale-o antes ou ajuste o script." >&2
    exit 1
fi

echo "uv encontrado em: $UV_BIN"
echo

# --- Precisa de sudo pra escrever em /etc/systemd/system --------------------
if [[ $EUID -ne 0 ]]; then
    SUDO="sudo"
else
    SUDO=""
fi

UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

# --- Gera o unit file --------------------------------------------------------
echo "Criando $UNIT_PATH ..."
$SUDO tee "$UNIT_PATH" > /dev/null <<EOF
[Unit]
Description=Purple Baka Chatbot - send_message
After=network-online.target
Wants=network-online.target

[Service]
Type=${SERVICE_TYPE}
User=${RUN_USER}
WorkingDirectory=${PROJECT_DIR}
Environment=PATH=${USER_HOME}/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=${UV_BIN} run ${SCRIPT_PATH}

[Install]
WantedBy=multi-user.target
EOF

# --- Habilita e inicia -------------------------------------------------------
echo "Recarregando systemd daemon..."
$SUDO systemctl daemon-reload

echo "Habilitando serviço no boot..."
$SUDO systemctl enable "$SERVICE_NAME.service"

echo "Iniciando serviço agora..."
$SUDO systemctl start "$SERVICE_NAME.service"

echo
echo "--- Status --------------------------------------------------------------"
$SUDO systemctl status "$SERVICE_NAME.service" --no-pager || true

echo
echo "Instalação concluída."
echo "Ver logs com: journalctl -u $SERVICE_NAME.service -f"
