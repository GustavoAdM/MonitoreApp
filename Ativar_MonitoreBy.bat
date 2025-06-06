@echo off
setlocal
chcp 1252 >nul

rem Define a pasta principal
set "main_folder=C:\Users\Belenzier\Desktop\WorkSpace\MonitoreBy"

echo ########## Inicinando limpeza cache 

rem Percorre todas as subpastas e verifica a exist ncia de __pycache__
for /r "%main_folder%" %%d in (.) do (
    if exist "%%d\__pycache__" (
        rd /s /q "%%d\__pycache__"
    )
)

echo ########## Opera  o de limpeza cache conclu da!

REM Verifica se a porta 8501 est  em uso
netstat -an | find ":8501" | find "LISTENING" >nul
if %errorlevel% == 0 (
    echo Streamlit j  est  ativo na porta 8501
    exit
) else (
    echo ########## Streamlit n o est  ativo. Iniciando...
    cd C:\Users\Belenzier\Desktop\WorkSpace\MonitoreBy
    call .\Core\Scripts\activate
    streamlit run .\MonitoreBy.py
)

pause
endlocal
