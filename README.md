# Concepts_of_programming_languages
Выполненные задания по курсу "Концепции языков программирования". Кафедра ABBYY (РИОТ), 8 семестр.

**Задание 1.** https://docs.google.com/document/d/13tRfk-zHVZI3vrTPr18OByHsu6AXzksYUTJauRSpSgo/

**Виртуальная машина, построенная на архитектуре фон Неймана.**

- Код реализации виртуальной машины представлен в файле **VirtualMachine.py**.

- Описание используемого человекочитаемого языка представлено в файле **instructions.txt**.

- Код ассемблера, переводящего описанные команды в бинарный формат, исполняемый машиной находится в файле **Assembler.py**.

- В файле **fib.asm** представлен пример программы на вспомогательном языке, реализующей вычисление n-го числа Фибоначчи.

- В файле **Disassembler.py** представлена реализация программы, которая переводит бинарный файл обратно в программу на вспомогательном языке.

- Пример вычисления n-го числа Фибоначчи на написанной виртуальной машине представлен в файле **working_example.ipynb**


*Дополнительно:* в файле fib.bin представлен результат работы ассемблера, в файле disasm_fib.asm - результат работы дизассемблера. В файле ВМ_dev можно посмотреть несколько низкоуровневых примеров работы отдельных модулей.


**Задание 2.** https://docs.google.com/document/d/1UkwWHDrgfwexiDy62zp8Oa0_x8oeK-HGzHvihoL9_vw/

**Реализация исключений.**

Добавлена система макросов TRY, CATCH, THROW, FINALIZE. После блока TRY может идти несколько блоков CATCH и обязательно блок FINALIZE (этот блок должен присутствовать даже если отсутствуют блоки CATCH).


**Задание 3.** https://docs.google.com/document/d/1T5CtOMT86w6YJp1nDWwt1wVeKq50nNfsST0hGtl-wMI/edit

**Реализация RTTI**

Добавлена система макросов USE_RTTI, TYPEID, BASE_PARENT, GET_CLASS_NAME.

USE_RTTI записывается перед объявлением класса, для которого подразумевается использование RTTI. Принимает в качестве параметров через запятую имя класса и его непосредственных предков.

BASE_PARENT должен записываться в качестве публичного предка каждого класса, для которого указан USE_RTTI.

Также каждый класс с указанием USE_RTTI должен содержать GET_CLASS_NAME, принимающий имя класса.

TYPEID в качестве параметра принимает объект любого типа, для которого был указан USE_RTTI, возвращает структуру typeId с информацией об объекте: можно с помощью набора методов получить имя класса, hash_code, также есть возможность сравнения.

Добавлена шаблонная функция DynamicCast совершающая приведения типов указателей друг к другу, если это возможно, и возвращающая nullptr иначе.

Примеры использования приведены в файле main.cpp в функции main.

**Семинар 10.05**
http://rextester.com/NTRWL28914
