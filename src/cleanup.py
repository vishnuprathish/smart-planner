import firebase_admin

# Delete all existing Firebase apps
for app in firebase_admin._apps:
    firebase_admin.delete_app(firebase_admin.get_app(app))
