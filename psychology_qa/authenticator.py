import streamlit_authenticator as stauth
import yaml


def get_auth() -> stauth.Authenticate:
    with open("psychology_qa/auth_config.yaml") as file:
        auth_config = yaml.safe_load(file)

    return stauth.Authenticate(**auth_config)
