# Fuzzing

Using fuzzing with <https://github.com/microsoft/restler-fuzzer>.

## To get it running

Put the a `swagger.json` in the root of the repo and add the folling lines to the Dockerfile:

```
COPY swagger.json .
COPY restler-quick-start.py .
```

```bash
cd /
python restler-quick-start.py --api_spec_path swagger.json --restler_drop_dir /RESTler
```

Check if trailing slashes are in `grammar.py`. If not, add them manually and only run commands like this (and not the quick start script).

```bash
dotnet "/RESTler/restler/Restler.dll" test / fuzz-lean / fuzz --grammar_file "Compile/grammar.py" --dictionary_file "Compile/dict.json" --settings "Compile/engine_settings.json" --no_ssl
```

## Add basic auth

```python
# /refresh.py
print("{u'Basic': {}}")
print("Authorization: Basic base64-encoded-string")
```

```bash
 dotnet "/RESTler/restler/Restler.dll" fuzz-lean --grammar_file "Compile/grammar.py" --dictionary_file "Compile/dict.json" --settings "Compile/engine_settings.json" --token_refresh_command "python /refresh.py" --token_refresh_interval 5000
```
