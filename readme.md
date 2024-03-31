## Instructions for Resolving Issue with Importing Functions from `werkzeug` Library (EN)

If you are experiencing an issue with importing the `secure_filename` and `FileStorage` functions from the `werkzeug` library, you need to make the following changes to the `__init__.py` file of the `werkzeug` library:

1. Open the `__init__.py` file of your installed `werkzeug` library. This file is typically located in the `site-packages/werkzeug/` directory in your Python installation.

2. Add the following lines at the top of the file:

    ```python
    from werkzeug.utils import secure_filename
    from werkzeug.datastructures import FileStorage
    ```

3. Save the file.

After making these changes, the `secure_filename` and `FileStorage` functions will be available for import from the `werkzeug` library anywhere in your application.

This instruction will help users quickly and easily resolve the issue with importing functions from `werkzeug` and continue working on their projects.


## Инструкция по решению проблемы с импортом функций из библиотеки `werkzeug` (RU)

Если у вас возникла проблема с импортом функций `secure_filename` и `FileStorage` из библиотеки `werkzeug`, вам необходимо внести следующие изменения в файл `__init__.py` этой библиотеки:

1. Откройте файл `__init__.py` вашей установленной библиотеки `werkzeug`. Обычно этот файл находится в папке `site-packages/werkzeug/` в вашей установке Python.

2. Добавьте следующие строки в верхней части файла:

    ```python
    from werkzeug.utils import secure_filename
    from werkzeug.datastructures import FileStorage
    ```

3. Сохраните файл.

После внесения этих изменений, функции `secure_filename` и `FileStorage` будут доступны для импорта из библиотеки `werkzeug` в любом месте вашего приложения.

Эта инструкция позволит пользователям быстро и легко решить проблему с импортом функций из `werkzeug` и продолжить работу над своим проектом.


