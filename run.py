from app import create_app
from get_ip import get_ip
app = create_app()
app.app_context().push()

if __name__=='__main__':
    # app.run(host=get_ip())
    app.run(debug=False) 