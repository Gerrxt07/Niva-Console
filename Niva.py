import Scripts.Core.Startup as Startup
from Scripts.Language.Language import language_loader, translate

# Initialize language settings
language_loader.load_config()
language_loader.load_translations()

print(translate("welcome_message"))

Startup.main()

print(translate("exit_message"))
