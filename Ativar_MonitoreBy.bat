@echo off
setlocal
chcp 1252 >nul

rem Define a pasta principal
set "main_folder=C:\AplicativosBelenzier\MonitoreBy"

echo ########## Inicinando limpeza cache 

rem Percorre todas as subpastas e verifica a existência de __pycache__
for /r "%main_folder%" %%d in (.) do (
    if exist "%%d\__pycache__" (
        rd /s /q "%%d\__pycache__"
    )
)

echo ########## Operação de limpeza cache concluída!

REM Verifica se a porta 8501 está em uso
netstat -an | find ":8501" | find "LISTENING" >nul
if %errorlevel% == 0 (
    echo Streamlit já está ativo na porta 8501
    exit
) else (
    echo ########## Streamlit não está ativo. Iniciando...
    cd C:\AplicativosBelenzier\MonitoreBy
    call .\Core\Scripts\activate
    streamlit run .\MonitoreBy.py
)

pause
endlocal
