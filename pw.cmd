@echo off
set cur_dir=%cd%
cd "%~dp0/.."
python -m pw %*
cd %cur_dir%