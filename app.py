from flask import Flask, session, redirect, request, render_template
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

SCOPES = ['https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/drive.metadata.readonly']

@app.route('/')
def index():
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=SCOPES,
            redirect_uri='http://127.0.0.1:3000/callback'
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
        )

        session['oauth_state'] = state

        # Redirige al URL de autorización de Google
        return redirect(authorization_url)

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/callback')
def callback():
    try:
        # Verifica el estado para prevenir ataques de CSRF
        stored_state = session.pop('oauth_state', None)
        received_state = request.args.get('state', None)

        if stored_state is None or received_state != stored_state:
            return 'Error de estado no válido', 400

        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=SCOPES,
            redirect_uri='http://127.0.0.1:3000/callback'
        )

        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials

        # Construye el servicio de la API de OAuth2
        service = build('oauth2', 'v2', credentials=creds)

        # Llama a la API para obtener información del perfil del usuario
        userinfo = service.userinfo().get().execute()

        return f"Usuario: {userinfo['name']}<br>Email: {userinfo['email']}"

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(port=3000)
