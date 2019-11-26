Web-приложении уже существует два пользователя:
1) login: admin		password: admin  - админимтратор web-приложения имеет доступ к созданию опросов
2) login: user		password: user 	 - обычный пользователь, может голосовать в опросах

API
- Добавить нового пользователя

https://poll-v1.herokuapp.com/api/user_add

POST запрос с параметрами в теле:
 - name - Имя пользователя
 - login - Логин пользователя 
 - password - Пароль пользователя

Ответ: 200 если все хорошо, 400 если пользователь существует или не все параметры переданны


- Получить опрос по id

https://poll-v1.herokuapp.com/api/poll/id

GET запрос

Ответ: json объект с ифнормацией о опросе


- Получить список всех опросов

https://poll-v1.herokuapp.com/api/poll
or
https://poll-v1.herokuapp.com/api/polls

GET запрос

Ответ: json объект со списком всех опросов



	
