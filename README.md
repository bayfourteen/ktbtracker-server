# King Tiger Black Belt Tracking System (ktbtracker)
REST API backend for the King Tiger Blackbelt Tracking System using FastAPI

## Language Support

Currently this product provides the ability to support three languages: English (en), Spanish (es), and Korean (ko).
Officially, only English is supported out-of-the-box at this time.

The Babel support structure for each of the three languages, English, Spanish and Korean, is already in place (init'd); 
do NOT run `pybabel init` since it will overwrite any translations already made.

### English Translations (Required)

To extract messages from source and templates, run the following commands from the project directory:
```bash
source .venv/bin/activate
pybabel extract -F src/babel.cfg -o messages.pot .
pybabel update -i src/messages.pot -d src/locales -l en
```

Modify the generated `.po` file (`src/locales/en/LC_MESSAGES/messages.po`) with the proper translations. Then compile
the `.po` file into the required `.mo` file:
```bash
source .venv/bin/activate
pybabel compile -d src/locales
```

### Spanish Translations (Optional)

To extract messages from source and templates, run the following commands from the project directory:
```bash
source .venv/bin/activate
pybabel extract -F src/babel.cfg -o messages.pot .
pybabel update -i src/messages.pot -d src/locales -l es
```

Modify the generated `.po` file (`src/locales/es/LC_MESSAGES/messages.po`) with the proper translations. Then compile
the `.po` file into the required `.mo` file:
```bash
source .venv/bin/activate
pybabel compile -d src/locales
```

### Korean Translations (Optional)

To extract messages from source and templates, run the following commands from the project directory:
```bash
source .venv/bin/activate
pybabel extract -F src/babel.cfg -o messages.pot .
pybabel update -i src/messages.pot -d src/locales -l ko
```

Modify the generated `.po` file (`src/locales/ko/LC_MESSAGES/messages.po`) with the proper translations. Then compile
the `.po` file into the required `.mo` file:
```bash
source .venv/bin/activate
pybabel compile -d src/locales
```
