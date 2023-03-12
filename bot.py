from botcity.web import WebBot, Browser, By
from botcity.plugins.telegram import BotTelegramPlugin
from botcity.plugins.gmail import BotGmailPlugin

import sys
import os
import pathlib
import time

from password import *

import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)



# BotCity Telegram Plugin
telegram = BotTelegramPlugin(token=bot)

#Diretorio Atual
diretorio = os.getcwd()

# credenciais email
credentials = 'cred.json'
gmail = BotGmailPlugin(credentials, 'tnoronha@3lackd.com')

#Captura os inputs do usuario em uma lista
lista_dados_telegram = []
usuario = ''


#TELEGRAM BOT WORKFLOW
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
VALOR_CNPJ, LOCAL, VALOR, SERVICO, OBSERVACOES, EMAIL, RESUMO = range(7)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    " DEFINE O INICIO DO FLUXO"
    reply_keyboard = [["EMITIR NFE"]]
    user = update.message.from_user
    usuario = user.username
    await update.message.reply_text(
        f"Olá, {user.first_name} sou eu o TelBot!O que vamos fazer hoje?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="digite /cancel para sair."
        ),
    )
    return VALOR_CNPJ


async def valor_cnpj(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Foi selecionado por %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "Poderia me enviar o CNPJ do cliente?"
    )

    return LOCAL


async def local(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("O CNPJ informado por %s: %s", user.first_name, update.message.text)
    validar_cnpj = update.message.text

    lista_dados_telegram.append(validar_cnpj)

    await update.message.reply_text(
        "Poderia me falar em que cidade foi executado o serviço?"
    )
    return VALOR


async def valor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    local_nota = update.message.text

    lista_dados_telegram.append(local_nota)

    logger.info("O local selecinado por %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "Poderia me falar o valor deste serviço?"
    )

    return SERVICO


async def servico(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("O valor selecionado por %s: %s", user.first_name, update.message.text)
    valor_nf = update.message.text

    lista_dados_telegram.append(valor_nf)

    await update.message.reply_text(
        "Poderia me falar o código deste serviço?"
    )

    return OBSERVACOES


async def observacoes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("O serviço selecionado por %s: %s", user.first_name, update.message.text)
    cod_nf_servico = update.message.text
    lista_dados_telegram.append(cod_nf_servico)

    await update.message.reply_text(
        "Poderia escrever as observações desta nota fiscal?"
    )

    return EMAIL


async def email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("As observações escritas por %s: %s", user.first_name, update.message.text)
    obs_nf = update.message.text
    lista_dados_telegram.append(obs_nf)

    await update.message.reply_text(
        "Poderia escrever o email de quem vai receber esta nota?"
    )

    return RESUMO


async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("O email escolhido por %s: %s", user.first_name, update.message.text)
    email_servico = update.message.text
    lista_dados_telegram.append(email_servico)
    resposta = [['OK']]

    await update.message.reply_text(
        f"AQUI ESTA O RESUMO:\nEMITIR NOTA PARA:{lista_dados_telegram[0]}\nLOCAL:{lista_dados_telegram[1]}\nVALOR: R$ {lista_dados_telegram[2]}\nCÓDIGO:{lista_dados_telegram[3]}\nOBSERVAÇÕES:{lista_dados_telegram[4]}\nDESTINATÁRIO:{lista_dados_telegram[5]}\nPressione OK para iniciar o processo ou digite /cancel para sair."
        , reply_markup=ReplyKeyboardMarkup(resposta, one_time_keyboard=True,
                                           input_field_placeholder='Digite /cancel para sair.'))

    Bot.main()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        f"{user.first_name}, estou encerrando conforme solicitado.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            VALOR_CNPJ: [MessageHandler(filters.Regex("^(EMITIR NFE)$"), valor_cnpj)],
            LOCAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, local)],
            VALOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, valor)],
            SERVICO: [MessageHandler(filters.TEXT & ~filters.COMMAND, servico)],
            OBSERVACOES: [MessageHandler(filters.TEXT & ~filters.COMMAND, observacoes)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            RESUMO: [MessageHandler(filters.TEXT & ~filters.COMMAND, resumo)]

        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


#BOT CITY WEBBOT
class Bot(WebBot):
    def action(self, execution=None):

        # Utiliza os inputs no Bot Telegram para emitir a nota
        cnpj_cliente = lista_dados_telegram[0]
        cidade_cliente = lista_dados_telegram[1]
        valor_round = lista_dados_telegram[2]

        if ',' in valor_round:
            valor_round.replace(',', '')
        if '.' in valor_round:
            valor_round.replace('.', '')

        observacoes_texto = lista_dados_telegram[4]
        destinatario = lista_dados_telegram[5]

        #Configurações do browser
        self.headless = False
        self.browser = Browser.FIREFOX
        self.driver_path = "C:\webdriver\geckodriver.exe"
        self.browse("http://guarulhos.ginfes.com.br/")
        self.maximize_window()

        #NAVEGAÇÃO PELO PORTAL GINFES GRU
        time.sleep(5)
        self.find_element(
            "//*[@id='principal']/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr["
            "1]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/tr/td[1]/img", By.XPATH).click()

        chave_cnpj = self.find_element("ext-gen29", By.NAME)
        chave_cnpj.send_keys(cnpj)
        senha_acesso = self.find_element("ext-gen33", By.NAME)
        senha_acesso.send_keys(senha)
        self.find_element('ext-gen51', By.ID).click()


        #aguarda um elemento para continuar a ação
        while not self.find_element('gwt-Image', By.CLASS_NAME):
            self.wait(5000)

        self.wait(5000)
        self.tab()
        self.enter()

        cliente = self.find_element("/html/body/div[1]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td["
                                    "2]/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/div/div/div/div/table["
                                    "1]/tbody/tr/td/div/div/div/form/fieldset/div/div/fieldset["
                                    "1]/div/div/table/tbody/tr[2]/td/div/div/div/div/div[1]/div/div/div/div[1]/input",
                                    By.XPATH)
        cliente.send_keys(cnpj_cliente)
        self.wait(1000)
        self.tab()
        self.enter()

        if self.find_element('//*[@id="ext-gen3865"]', By.XPATH):
            self.enter()
            print('Cnpj inválido, confira os dados e tente novamente')
            self.stop_browser()
            sys.exit()

        self.wait(5000)

        check_box = self.find_element("/html/body/div[1]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td["
                                      "2]/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/div/div/div/div/table["
                                      "1]/tbody/tr/td/div/div/div/form/fieldset/div/div/fieldset[4]/div/div/div/div["
                                      "1]/div/label", By.XPATH)
        check_box.click()

        next = self.find_element("/html/body/div[1]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td["
                                 "2]/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/div/div/div/div/table["
                                 "2]/tbody/tr/td/table/tbody/tr/td[2]/em/button", By.XPATH)
        next.click()

        estado_servico = ''

        cidade_servico = self.find_element('/html/body/div[1]/table/tbody/tr[2]/td/table/tbody/tr['
                                           '2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr/td/div/div['
                                           '2]/div/div[2]/div/div/div/div/div/form/fieldset['
                                           '2]/div/div/div/div/div/div/div[2]/div/div/div/div[1]/div/input', By.XPATH)
        cidade_servico.clear()
        cidade_servico.send_keys(cidade_cliente)
        self.tab()

        self.type_down()
        self.enter()

        self.control_a()
        self.control_c()
        codigo_selecionado = self.get_clipboard()

        quadro_observacoes = self.find_element('/html/body/div[1]/table/tbody/tr[2]/td/table/tbody/tr['
                                               '2]/td/table/tbody/tr/td['
                                               '2]/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/div/div['
                                               '2]/div/div/div/div/div/form/fieldset[3]/div/div/div['
                                               '2]/div/div/div/div[1]/div/div/div/div[1]/textarea', By.XPATH)
        quadro_observacoes.clear()
        quadro_observacoes.send_keys(observacoes_texto)

        valor_servico = self.find_element('/html/body/div[1]/table/tbody/tr[2]/td/table/tbody/tr['
                                          '2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr/td/div/div['
                                          '2]/div/div[2]/div/div/div/div/div/form/fieldset[5]/div/div/div['
                                          '1]/div/div/div/div[1]/div/div/div/div[1]/input', By.XPATH)
        valor_servico.send_keys(valor_round)

        self.tab()
        self.enter()

        proximo = self.find_element('/html/body/div[1]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td['
                                    '2]/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/div/div['
                                    '2]/div/div/div/div/div/form/table/tbody/tr/td['
                                    '2]/table/tbody/tr/td/table/tbody/tr/td[2]/em/button', By.XPATH)
        proximo.click()


        emitir = self.find_element('/html/body/div[1]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td['
                                   '2]/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/div/div['
                                   '3]/div/div/div/div/div/form/table[2]/tbody/tr/td['
                                   '2]/table/tbody/tr/td/table/tbody/tr/td[2]/em/button', By.XPATH)

        #sequencia de ações para capturar elementos flutuantes acima da pagina. O tempo de espera garante que eles serão pegos
        emitir.click()
        time.sleep(5)
        self.enter()
        time.sleep(5)
        self.enter()
        time.sleep(5)

        #Se prepara para trocar de aba, quando a nota fiscal é impressa em pdf.
        abas = self.get_tabs()
        lista = abas[1]
        #ativa a seguda pagina como principal e continua o proceso
        self.activate_tab(lista)
        time.sleep(10)

        self.tab()
        self.enter()

        self.wait(10000)

        # finaliza o browser
        self.stop_browser()

        #EMISSÃO PELO GMAIL COM BOTCITY GMAIL PLUGIN
        assunto = f"Emissão de Nota para {cnpj_cliente}"
        corpo = f'Olá, segue anexo a nota fiscal dos serviços prestados pelo CNPJ: {cnpj}'
        destinatario = lista_dados_telegram[5]

        arquivo = pathlib.Path(diretorio).glob("*.pdf")
        lista_nota = []

        for i in arquivo:
            lista_nota.append(i)

        caminho = str(lista_nota[0])

        gmail.send_message(assunto, corpo, [destinatario], attachments=[caminho], use_html=False)
        sucesso = f'Mensagem enviada com sucesso para {destinatario}, com o anexo {caminho}.'



        #avisa no grupo do Telegram que o envio foi um sucesso
        telegram.send_message(
            text= f'Olá! {usuario}\n{sucesso}.\nDados prontos para você verificar.',
            group="TelbotGroup",
            username=["@NfeGruBot"]
        )

        telegram.upload_document(document=caminho,group='TelbotGroup',caption=f'Nota fiscal:{cnpj}')

        # remove o arquivo após envio
        os.remove(caminho)






if __name__ == '__main__':
    main()


