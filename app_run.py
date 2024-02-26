from var2 import app, db


if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == '__main__': # для создания бд
#     app.app_context().push()
#     db.create_all()
#     print("База создана")
