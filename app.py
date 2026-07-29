import telebot
from telebot import apihelper  # Importamos el ayudante de la API
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
# 🔥 ACTIVACIÓN OBLIGATORIA DE MIDDLEWARES (Debe ir antes de crear el objeto 'bot')
apihelper.ENABLE_MIDDLEWARE = True
from telethon import TelegramClient, events
import asyncio
import os
import threading
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
#from dotenv import load_dotenv #  --------------ESTO SE ACTIVA SOL PARA PRUEBAS

# Esto carga las variables del archivo .env en la memoria del sistema operativo
#load_dotenv()

# --- LIBRERÍAS PARA EL SERVIDOR WEB FALSO (REQUERIDO POR RENDER) --- --------------ESTO SE ACTIVA SOL PARA PRUEBAS
class FakeServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("BOT HUGO ACTUALIZADO - VERSION 3.2 🚀".encode("utf-8"))

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()

def iniciar_servidor_falso():
    puerto = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', puerto), FakeServer)
    print(f"📡 Servidor de simulación escuchando en el puerto {puerto}")
    server.serve_forever()

# Iniciamos el servidor HTTP obligatorio para Render
threading.Thread(target=iniciar_servidor_falso, daemon=True).start()


# --- CONFIGURACIÓN SEGURA MEDIANTE VARIABLES DE ENTORNO ---
# En Render, configura estas variables en la sección "Environment" de tu servicio.
# Al quitar los valores por defecto, tu código queda 100% blindado contra filtraciones.
try:
    API_ID = int(os.environ["API_ID"])  
    API_HASH = os.environ["API_HASH"]  
    BOT_TOKEN = os.environ["BOT_TOKEN"]  
except KeyError as e:
    raise ValueError(f"❌ ERROR CRÍTICO DE SEGURIDAD: Falta configurar la variable de entorno obligatoria: {e} en Render.")

# 🔍 PALABRAS CLAVE PARA ENCONTRAR LOS GRUPOS TRADICIONALES
TXT_FRANCHESCO = "FRANCHESCO"
TXT_DF_VIP     = "DF VIP"
TXT_KIMICO     = "KIMICO"  # Nueva palabra clave para el grupo Kimico

# 🤖 USERNAMES PARA LOS BOTS DIRECTOS CHAT UNO A UNO
USER_NORTH_BOT = "northdatabasicbot"
USER_LIAM_BOT  = "Yinwodataa_botx"  

from telethon.sessions import StringSession

# Recuperamos la sesión en texto plano desde las variables de entorno de Render
SESSION_STRING = os.environ.get("SESSION_STRING", None)

bot = telebot.TeleBot(BOT_TOKEN)

# 🔄 MIDDLEWARE DE TRADUCCIÓN: Convierte comandos a minúsculas automáticamente
@bot.middleware_handler(update_types=['message'])
def normalizar_comandos_minusculas(bot_instance, message):
    if message.text and message.text.startswith('/'):
        partes = message.text.split(maxsplit=1)
        comando_minuscula = partes[0].lower()
        if len(partes) > 1:
            message.text = f"{comando_minuscula} {partes[1]}"
        else:
            message.text = comando_minuscula

if SESSION_STRING:
    print("🔐 Iniciando Telethon mediante StringSession...")
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    print("📁 Usando sesión por archivo local (Modo Desarrollo)...")
    client = TelegramClient('sesion_hugo', API_ID, API_HASH)

chat_id_hugo = None
loop_principal = None  

entidad_franchesco = None
entidad_df_vip     = None
entidad_north_bot  = None  
entidad_liam_bot   = None
entidad_kimico     = None  # Nueva entidad

id_franchesco = None
id_df_vip     = None
id_north_bot  = None
id_liam_bot   = None
id_kimico     = None  # Nuevo ID

control_operaciones = {}
north_respondido_exito = {} 
imagenes_procesadas_recientes = []  

async def mapear_motores_por_id():
    global entidad_franchesco, entidad_df_vip, entidad_north_bot, entidad_liam_bot, entidad_kimico
    global id_franchesco, id_df_vip, id_north_bot, id_liam_bot, id_kimico

    if not client.is_connected():
        await client.connect()

    print("📋 Sincronizando e indexando IDs reales de Telegram...")

    # 🛑 ACTUALIZADO: Limpiamos los grupos obsoletos de la lista negra
    GRUPOS_A_OBVIAR = ["CANAL FRANCHESCO DATA SAC", "FRANCHESCO MASTER", "DF VIP [ GRUPO 05 ]"]

    async for dialog in client.iter_dialogs(limit=150):
        if dialog.name:
            nombre_chat = dialog.name.upper().strip()
            if any(obviar.upper() in nombre_chat for obviar in GRUPOS_A_OBVIAR):
                continue

            if TXT_FRANCHESCO in nombre_chat and not entidad_franchesco:
                entidad_franchesco = dialog.input_entity
                id_franchesco = dialog.id
                print(f"🎯 ID Franchesco Fijado: {id_franchesco} ({dialog.name})") 

            # 🚀 CORRECCIÓN: Captura el nuevo grupo DF VIP 03 asegurando que coincida el texto
            elif TXT_DF_VIP in nombre_chat and "03" in nombre_chat and not entidad_df_vip:
                entidad_df_vip = dialog.input_entity
                id_df_vip = dialog.id
                print(f"🎯 ID DF VIP 03 Fijado: {id_df_vip} ({dialog.name})")

            elif TXT_KIMICO in nombre_chat and not entidad_kimico:
                entidad_kimico = dialog.input_entity
                id_kimico = dialog.id
                print(f"🎯 ID KIMICO Grupo Fijado: {id_kimico} ({dialog.name})")

    try:
        entidad_north_bot = await client.get_input_entity(USER_NORTH_BOT)
        full_north = await client.get_entity(entidad_north_bot)
        id_north_bot = full_north.id
        print(f"🎯 ID North Bot Fijado: {id_north_bot} (@{USER_NORTH_BOT})")
    except Exception as e:
        print(f"⚠️ Alerta North Bot: {e}")

    try:
        entidad_liam_bot = await client.get_input_entity(USER_LIAM_BOT)
        full_liam = await client.get_entity(entidad_liam_bot)
        id_liam_bot = full_liam.id
        print(f"🎯 ID Liam Bot Fijado: {id_liam_bot} (@{USER_LIAM_BOT})")
    except Exception as e:
        print(f"⚠️ Alerta Liam: {e}")

async def flujo_especial_north(placa, clave_operacion):
    global entidad_north_bot, north_respondido_exito, control_operaciones
    if not entidad_north_bot: return

    north_respondido_exito[clave_operacion] = False

    print(f"⏱️ [NORTH DATA] Enviando primer paso /pla {placa} para {clave_operacion}")
    try:
        await client.send_message(entidad_north_bot, f"/pla {placa}")
    except Exception as e: 
        print(f"❌ Error al enviar /pla a North: {e}")

    await asyncio.sleep(30)

    # Si la operación sigue activa, ejecutamos el segundo paso (/tive)
    if clave_operacion in control_operaciones:
        print(f"🔄 [NORTH DATA] Pasaron 30s. Ejecutando segundo paso con /tive {placa}")
        try:
            await client.send_message(entidad_north_bot, f"/tive {placa}")
        except Exception as e: 
            print(f"❌ Error en envío de /tive a North: {e}")

def liberar_operacion_de_memoria(clave_operacion):
    global control_operaciones, north_respondido_exito
    if clave_operacion in control_operaciones:
        msg_carga = control_operaciones[clave_operacion].get("msg_carga")
        if msg_carga:
            try:
                bot.delete_message(msg_carga.chat.id, msg_carga.message_id)
            except: pass

        del control_operaciones[clave_operacion]
        print(f"🧹 [MEMORIA] Operación [{clave_operacion}] liberada de forma aislada.")

    if clave_operacion in north_respondido_exito: 
        del north_respondido_exito[clave_operacion]

async def timeout_seguridad_operacion(clave_operacion, segundos=90):
    await asyncio.sleep(segundos)
    global control_operaciones
    if clave_operacion in control_operaciones:
        print(f"⏱️ [TIME-OUT] Forzando liberación de [{clave_operacion}] por inactividad ({segundos}s).")
        liberar_operacion_de_memoria(clave_operacion)

def verificar_y_marcar_respuesta(clave_operacion, motor):
    global control_operaciones
    if clave_operacion not in control_operaciones:
        return

    if motor in control_operaciones[clave_operacion]["motores"]:
        control_operaciones[clave_operacion]["motores"][motor] = True
        print(f"📊 [PROGRESO {clave_operacion}]: {motor} -> ✅ REGISTRADO.")

    if all(control_operaciones[clave_operacion]["motores"].values()):
        liberar_operacion_de_memoria(clave_operacion)


# =====================================================================
# --- 🔥 SECCIÓN DE COMANDOS INDEPENDIENTES ---
# =====================================================================

@bot.message_handler(commands=['partida'])
def recibir_orden_docs(message):
    global chat_id_hugo, entidad_df_vip, loop_principal, control_operaciones
    chat_id_hugo = message.chat.id  
    texto = message.text.split()
    if len(texto) < 2:
        bot.reply_to(message, "❌ Envía la placa o partida. Ejemplo: /partida CAJ270")
        return

    placa = texto[1].upper().strip().replace("-", "").replace(" ", "")
    clave_operacion = f"{placa}_PARTIDA"

    if entidad_df_vip:
        msg_carga = bot.reply_to(message, f"🔍 Consultando PDF para {placa} en DF VIP...")
        control_operaciones[clave_operacion] = {
            "placa": placa,
            "origen": "PARTIDA",
            "msg_carga": msg_carga,
            "motores": {"DF VIP": False}
        }
        if loop_principal:
            asyncio.run_coroutine_threadsafe(client.send_message(entidad_df_vip, f"/PARTIDAV {placa}"), loop_principal)
            asyncio.run_coroutine_threadsafe(timeout_seguridad_operacion(clave_operacion, 90), loop_principal)

@bot.message_handler(commands=['placa'])
def recibir_orden_imagenes(message):
    global chat_id_hugo, entidad_north_bot, loop_principal, control_operaciones
    chat_id_hugo = message.chat.id  
    texto = message.text.split()
    if len(texto) < 2:
        bot.reply_to(message, "❌ Envía la placa. Ejemplo: /placa CAJ270")
        return

    placa = texto[1].upper().strip().replace("-", "").replace(" ", "")
    clave_operacion = f"{placa}_PLACA"

    if entidad_north_bot:
        msg_carga = bot.reply_to(message, f"📸 Consultando en NORTH DATA para {placa}...")
        control_operaciones[clave_operacion] = {
            "placa": placa,
            "origen": "PLACA",
            "msg_carga": msg_carga,
            "motores": {"NORTH DATA": False}
        }
        if loop_principal:
            asyncio.run_coroutine_threadsafe(client.send_message(entidad_north_bot, f"/pla {placa}"), loop_principal)
            asyncio.run_coroutine_threadsafe(timeout_seguridad_operacion(clave_operacion, 90), loop_principal)

@bot.message_handler(commands=['tive'])
def recibir_orden_tive_global(message):
    global chat_id_hugo, loop_principal, control_operaciones
    global entidad_df_vip, entidad_franchesco, entidad_north_bot, entidad_liam_bot, entidad_kimico

    chat_id_hugo = message.chat.id  
    texto = message.text.split()
    if len(texto) < 2:
        bot.reply_to(message, "❌ Envía la placa. Ejemplo: /tive CAJ270")
        return

    placa = texto[1].upper().strip().replace("-", "").replace(" ", "")
    clave_operacion = f"{placa}_TIVE"
    msg_carga = bot.reply_to(message, f"⚡ ¡Ráfaga /tive activada para {placa}!\nDisparando consultas a todos los proveedores...")

    if not loop_principal: return
    control_operaciones[clave_operacion] = {
        "placa": placa,
        "origen": "TIVE",
        "msg_carga": msg_carga,
        "motores": {
            "DF VIP": False,
            "FRANCHESCO": False,
            "NORTH DATA": False,
            "LIAM DATA": False,
            "KIMICO": False  # Se añade KIMICO al control de respuestas
        }
    }

    if entidad_franchesco:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_franchesco, f"/tive {placa}"), loop_principal)
    if entidad_df_vip:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_df_vip, f"/tive {placa}"), loop_principal)
    if entidad_north_bot:
        asyncio.run_coroutine_threadsafe(flujo_especial_north(placa, clave_operacion), loop_principal)
    if entidad_liam_bot:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_liam_bot, f"/tive {placa}"), loop_principal)
    if entidad_kimico:
        # Para el grupo KIMICO enviamos el comando alternativo /pla
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_kimico, f"/pla {placa}"), loop_principal)

    asyncio.run_coroutine_threadsafe(timeout_seguridad_operacion(clave_operacion, 90), loop_principal)

@bot.message_handler(commands=['boleta'])
def recibir_orden_boleta_global(message):
    global chat_id_hugo, loop_principal, control_operaciones
    global entidad_df_vip, entidad_franchesco, entidad_north_bot, entidad_liam_bot

    chat_id_hugo = message.chat.id  
    texto = message.text.split()
    if len(texto) < 2:
        bot.reply_to(message, "❌ Envía la placa. Ejemplo: /boleta CAJ270")
        return

    placa = texto[1].upper().strip().replace("-", "").replace(" ", "")
    clave_operacion = f"{placa}_BOLETA"
    msg_carga = None
    try:
        msg_carga = bot.reply_to(message, f"🧾 ¡Ráfaga /boleta activada para {placa}!\nDisparando consultas de boletas informativas...")
    except Exception as network_error:
        print(f"⚠️ Aviso: Retardo en la red al enviar mensaje de carga: {network_error}")

    if not loop_principal: return
    control_operaciones[clave_operacion] = {
        "placa": placa,
        "origen": "BOLETA", 
        "msg_carga": msg_carga,
        "motores": {
            "DF VIP": False,
            "FRANCHESCO": False,
            "NORTH DATA": False,
            "LIAM DATA": False,
            "KIMICO": False
        }
    }

    if entidad_franchesco:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_franchesco, f"/boi {placa}"), loop_principal)
    if entidad_df_vip:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_df_vip, f"/boi {placa}"), loop_principal)
    if entidad_liam_bot:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_liam_bot, f"/bolif {placa}"), loop_principal)
    if entidad_north_bot:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_north_bot, f"/bolinf {placa}"), loop_principal)
    # CONDICIÓN para que también le escriba a Kimico
    if entidad_kimico:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_kimico, f"/boleta {placa}"), loop_principal)

    asyncio.run_coroutine_threadsafe(timeout_seguridad_operacion(clave_operacion, 90), loop_principal)

@bot.message_handler(commands=['propiedades'])
def recibir_orden_partidadni_global(message):
    global chat_id_hugo, loop_principal, control_operaciones
    global entidad_df_vip, entidad_franchesco

    chat_id_hugo = message.chat.id  
    texto = message.text.split()
    if len(texto) < 2:
        bot.reply_to(message, "❌ Envía el DNI. Ejemplo: /propiedades 12345678")
        return

    dni = texto[1].upper().strip()
    clave_operacion = f"{dni}_PARTIDADNI" 
    msg_carga = None
    try:
        msg_carga = bot.reply_to(message, f"📑 ¡Ráfaga /propiedades activada para DNI: {dni}!\nDisparando consultas de Propiedades PDF...")
    except Exception as network_error:
        print(f"⚠️ Aviso: Retardo en la red al enviar mensaje de carga: {network_error}")

    if not loop_principal: return
    control_operaciones[clave_operacion] = {
        "placa": dni,
        "origen": "PARTIDADNI", 
        "msg_carga": msg_carga,
        "motores": {
            "DF VIP": False,
            "FRANCHESCO": False
        }
    }

    if entidad_franchesco:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_franchesco, f"/propdf {dni}"), loop_principal)
    if entidad_df_vip:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_df_vip, f"/propdf {dni}"), loop_principal)

    asyncio.run_coroutine_threadsafe(timeout_seguridad_operacion(clave_operacion, 90), loop_principal)

@bot.message_handler(commands=['nombre'])
def recibir_orden_nombre_global(message):
    global chat_id_hugo, loop_principal, control_operaciones
    global entidad_df_vip, entidad_franchesco

    chat_id_hugo = message.chat.id  
    texto_completo = message.text.split(maxsplit=1)
    if len(texto_completo) < 2:
        bot.reply_to(message, "❌ Envía el nombre completo. Ejemplo: /nombre CRISTIAN CONDORI MONTOYA")
        return

    nombre_original = texto_completo[1].upper().strip()
    palabras = nombre_original.split()
    nombre_formateado = " | ".join(palabras)
    clave_operacion = f"{''.join(palabras)}_NOMBRE" 

    msg_carga = None
    try:
        msg_carga = bot.reply_to(message, f"👤 ¡Búsqueda por Nombre activada para: {nombre_original}!\nFormato enviado: `/nm {nombre_formateado}`\nDisparando consultas...")
    except Exception as network_error:
        print(f"⚠️ Aviso: Retardo en la red al enviar mensaje de carga: {network_error}")

    if not loop_principal: return
    control_operaciones[clave_operacion] = {
        "placa": "".join(palabras), 
        "origen": "NOMBRE", 
        "msg_carga": msg_carga,
        "motores": {
            "DF VIP": False,
            "FRANCHESCO": False
        }
    }

    if entidad_franchesco:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_franchesco, f"/nm {nombre_formateado}"), loop_principal)
    if entidad_df_vip:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_df_vip, f"/nm {nombre_formateado}"), loop_principal)

    asyncio.run_coroutine_threadsafe(timeout_seguridad_operacion(clave_operacion, 120), loop_principal)

@bot.message_handler(commands=['denuncias'])
def recibir_orden_denuncias_global(message):
    global chat_id_hugo, loop_principal, control_operaciones
    global entidad_df_vip, entidad_franchesco

    chat_id_hugo = message.chat.id  
    texto = message.text.split()
    if len(texto) < 2:
        bot.reply_to(message, "❌ Envía la placa. Ejemplo: /denuncias CAJ270")
        return

    placa = texto[1].upper().strip().replace("-", "").replace(" ", "")
    clave_operacion = f"{placa}_DENUNCIAS"

    msg_carga = None
    try:
        msg_carga = bot.reply_to(message, f"🚨 ¡Ráfaga /denuncias activada para {placa}!\nDisparando consultas de antecedentes policiales y denuncias...")
    except Exception as network_error:
        print(f"⚠️ Aviso: Retardo en la red al enviar mensaje de carga: {network_error}")

    if not loop_principal: return
    control_operaciones[clave_operacion] = {
        "placa": placa,
        "origen": "DENUNCIAS", 
        "msg_carga": msg_carga,
        "motores": {
            "DF VIP": False,
            "FRANCHESCO": False
        }
    }

    if entidad_franchesco:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_franchesco, f"/denpla {placa}"), loop_principal)
    if entidad_df_vip:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_df_vip, f"/denunv {placa}"), loop_principal)

    asyncio.run_coroutine_threadsafe(timeout_seguridad_operacion(clave_operacion, 90), loop_principal)

@bot.message_handler(commands=['rq'])
def recibir_orden_rq_global(message):
    global chat_id_hugo, loop_principal, control_operaciones
    global entidad_north_bot, entidad_kimico

    chat_id_hugo = message.chat.id  
    texto = message.text.split()
    if len(texto) < 2:
        bot.reply_to(message, "❌ Envía la placa. Ejemplo: /rq CAJ270")
        return

    placa = texto[1].upper().strip().replace("-", "").replace(" ", "")
    clave_operacion = f"{placa}_RQ"

    msg_carga = None
    try:
        msg_carga = bot.reply_to(message, f"🔍 ¡Consulta /rq activada para {placa}!\nDisparando solicitudes a North Data y Kimico...")
    except Exception as network_error:
        print(f"⚠️ Aviso: Retardo en la red al enviar mensaje de carga: {network_error}")

    if not loop_principal: return
    control_operaciones[clave_operacion] = {
        "placa": placa,
        "origen": "RQ", 
        "msg_carga": msg_carga,
        "motores": {
            "NORTH DATA": False,
            "KIMICO": False
        }
    }

    if entidad_north_bot:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_north_bot, f"/rqpla {placa}"), loop_principal)
    if entidad_kimico:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_kimico, f"/rqpla {placa}"), loop_principal)

    asyncio.run_coroutine_threadsafe(timeout_seguridad_operacion(clave_operacion, 90), loop_principal)

# =====================================================================
# --- 🎛️ PANEL INTERACTIVO Y LOGICA DE BOTONES ---
# =====================================================================

def generar_menu_principal(first_name):
    markup = InlineKeyboardMarkup(row_width=2)

    msg_ayuda = urllib.parse.quote("NECESITO AYUDA POR FAVOR LLAMAME")
    msg_avisar = urllib.parse.quote("hay algo que no esta funcionando bien")
    msg_urgencia = urllib.parse.quote("por favor llamame urgente tengo unos problemas")

    numero_whatsapp = "51952513161"

    btn_ayuda = InlineKeyboardButton("🆘 AYUDA", url=f"https://wa.me/{numero_whatsapp}?text={msg_ayuda}")
    btn_avisar = InlineKeyboardButton("📢 AVISAR", url=f"https://wa.me/{numero_whatsapp}?text={msg_avisar}")
    btn_urgencia = InlineKeyboardButton("🚨 URGENCIA", url=f"https://wa.me/{numero_whatsapp}?text={msg_urgencia}")
    btn_vehiculos = InlineKeyboardButton("🚙 VEHICULOS", callback_data="menu_vehiculos")

    markup.add(btn_vehiculos, btn_ayuda)
    markup.add(btn_avisar, btn_urgencia)

    texto = (
        f"Hola, <b>{first_name}</b>\n\n"
        "💻 <b>[ PANEL DE COMANDOS ]</b>\n\n"
        "Bienvenido a este <b>BOT VEHICULAR </b>de uso exclusivo para informes y sacar documentos especificos muy constantes a un click. \n\n "
        " ✅ Creado y diseñado por mi 👨‍💻\n\n"
        "<b>Selecciona una opción según la categoría que deseas explorar.</b>\n\n"
    )
    return texto, markup

@bot.message_handler(commands=['start', 'menu', 'cmds'])
def enviar_panel_comandos(message):
    texto, markup = generar_menu_principal(message.from_user.first_name)
    bot.send_message(message.chat.id, texto, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def responder_clicks_botones(call):
    if call.data == "menu_vehiculos":
        markup_vehiculos = InlineKeyboardMarkup()
        btn_regresar = InlineKeyboardButton("⬅️ Volver al Menú", callback_data="volver_principal")
        markup_vehiculos.add(btn_regresar)

        texto_vehiculos = (
            "📋 <b>[ CATEGORÍA ⇒ VEHÍCULOS ]</b>\n\n"
            "1️⃣ <b>CONSULTA PARTIDA DEL VEHICULO (DF VIP)</b>\n"
            "• Comando: /partida [placa] \n"
            "• Ejemplo: /partida CAJ270 \n\n"
            "2️⃣ <b>CONSULTA PLACA (FRANCHESCO)</b>\n"
            "• Comando: /placa [placa] \n"
            "• Ejemplo: /placa CAJ270 \n\n"
            "3️⃣ <b>BUSQUEDA TIVE EN BOTS</b>\n"
            "• Comando: /tive [placa] \n"
            "• Ejemplo: /tive CAJ270 \n\n"
            "4️⃣ <b>BUSQUEDA BOLETAS INFORMATIVAS</b>\n"
            "• Comando: /boleta [placa] \n"
            "• Ejemplo: /boleta CAJ270 \n\n"
            "5️⃣ <b>BUSQUEDA DENUNCIAS DEL VEHICULO</b>\n"
            "• Comando: /denuncias [placa] \n"
            "• Ejemplo: /denuncias CAJ270 \n\n"
            "6️⃣ <b>BUSCA TODAS LAS PROPIEDADES POR DNI</b>\n"
            "• Comando: /propiedades [DNI] \n"
            "• Ejemplo: /propiedades 44556677\n\n"
            "7️⃣ <b>BUSCA EL DNI POR NOMBRE </b>\n"
            "• Comando: /nombre [NOMBRE Y APELLIDO] \n"
            "• Ejemplo: /nombre Cristian Condori Montoya\n\n"
            "8️⃣ <b>CONSULTA REQUERIMIENTO (RQ)</b>\n"
            "• Comando: /rq [placa] \n"
            "• Ejemplo: /rq CAJ270"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=texto_vehiculos, parse_mode="HTML", reply_markup=markup_vehiculos)

    elif call.data == "volver_principal":
        bot.answer_callback_query(call.id)
        texto_menu, markup_menu = generar_menu_principal(call.from_user.first_name)
        bot.edit_message_text(
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            text=texto_menu, 
            parse_mode="HTML", 
            reply_markup=markup_menu
        )

    elif call.data.startswith("prov_"):
        partes = call.data.split("_")
        if len(partes) < 4: return

        prov_chat_id = int(partes[1])
        prov_msg_id = int(partes[2])
        boton_data_hex = partes[3]
        boton_data_bytes = bytes.fromhex(boton_data_hex)

        bot.answer_callback_query(call.id, text="⏳ Solicitando documento al proveedor...")

        if loop_principal:
            async def presionar_boton_remoto():
                try:
                    mensaje_remoto = await client.get_messages(prov_chat_id, ids=prov_msg_id)
                    if mensaje_remoto and mensaje_remoto.reply_markup:
                        for i, row in enumerate(mensaje_remoto.reply_markup.rows):
                            for j, button in enumerate(row.buttons):
                                if hasattr(button, 'data') and button.data == boton_data_bytes:
                                    print(f"⚡ [CLICK AUTOMÁTICO] Pulsando botón '{button.text}' en la posición [{i}][{j}] del proveedor...")
                                    await mensaje_remoto.click(i, j)
                                    return
                    print("❌ No se encontró el botón equivalente en el mensaje del proveedor.")
                except Exception as e:
                    print(f"❌ Error al replicar el click en el proveedor: {e}")

            asyncio.run_coroutine_threadsafe(presionar_boton_remoto(), loop_principal)

import time

def arrancar_bot_padre():
    # 1. Eliminamos cualquier webhook o consultas colgadas en los servidores de Telegram
    try:
        print("🗑️ Limpiando consultas previas en Telegram para evitar conflictos...")
        bot.remove_webhook()
    except Exception as e:
        print(f"⚠️ Aviso al limpiar Webhook: {e}")

    # 2. Bucle infinito controlado contra el Error 409
    while True:
        try:
            print("🤖 Servidor Telebot iniciando polling infinity...")
            # En pyTelegramBotAPI, para ignorar mensajes viejos acumulados en ráfaga se usa 'none_stop=True' 
            # y se le pasan los parámetros de control correctos sin romper el constructor.
            bot.infinity_polling(
                timeout=60, 
                long_polling_timeout=60, 
                logger_level=50
            )
        except Exception as e:
            error_msg = str(e)
            if "Conflict" in error_msg or "409" in error_msg:
                print("⏳ Conflicto 409 activo (Render aún está apagando la versión anterior). Reintentando en 8 segundos...")
                time.sleep(8)
            else:
                print(f"❌ Error en hilo de Telebot: {e}. Reiniciando en 5s...")
                time.sleep(5)


# --- FUNCIÓN PRINCIPAL ASÍNCRONA ---
async def main():
    global loop_principal, control_operaciones, north_respondido_exito
    global id_franchesco, id_df_vip, id_north_bot, id_liam_bot
    loop_principal = asyncio.get_running_loop()

    await mapear_motores_por_id()

    @client.on(events.NewMessage())
    async def escuchador_global_mensajes(event):
        global chat_id_hugo, control_operaciones, north_respondido_exito
        global id_franchesco, id_df_vip, id_north_bot, id_liam_bot, id_kimico

        chat_actual_id = event.chat_id
        if not chat_id_hugo or not control_operaciones:
            return

        origen_texto = "DESCONOCIDO"

        if id_franchesco and chat_actual_id == id_franchesco: origen_texto = "FRANCHESCO"
        elif id_df_vip and chat_actual_id == id_df_vip: origen_texto = "DF VIP"
        elif id_north_bot and chat_actual_id == id_north_bot: origen_texto = "NORTH DATA"
        elif id_liam_bot and chat_actual_id == id_liam_bot: origen_texto = "LIAM DATA"
        elif id_kimico and chat_actual_id == id_kimico: origen_texto = "KIMICO"  # Identifica el grupo

        if origen_texto == "DESCONOCIDO": return

        op_encontrada = None
        placa_detectada = None

        texto_a_buscar = ""
        if event.message.text:
            texto_a_buscar = event.message.text.upper()
        if event.message.media and event.message.document:
            for attr in event.message.document.attributes:
                if hasattr(attr, 'file_name') and attr.file_name:
                    texto_a_buscar += " " + attr.file_name.upper()

        for clave, op_data in list(control_operaciones.items()):
            if op_data["placa"] in texto_a_buscar.replace("-", "").replace("_", "").replace(" ", "").replace("|", ""):
                if origen_texto in op_data["motores"]:
                    op_encontrada = clave
                    placa_detectada = op_data["placa"]
                    break

        if not op_encontrada:
            for clave, op_data in list(control_operaciones.items()):
                if origen_texto in op_data["motores"] and not op_data["motores"][origen_texto]:

                    if op_data["origen"] == "NOMBRE":
                        if texto_a_buscar.strip().startswith("/"):
                            continue

                        palabras_validas_nombre = ["DNI", "NOMBRES", "APELLIDOS", "RESULTADOS", "NO SE ENCONTRÓ", "NO SE ENCONTRO", "ERROR", "NO EXISTE", "ANTI-SPAM"]
                        if any(palabra in texto_a_buscar.upper() for palabra in palabras_validas_nombre):
                            op_encontrada = clave
                            placa_detectada = op_data["placa"]
                            break
                        else:
                            continue

                    if origen_texto == "NORTH DATA" or origen_texto == "LIAM DATA":
                        if op_data["origen"] in ["TIVE", "BOLETA", "RQ"]: 
                            op_encontrada = clave
                            placa_detectada = op_data["placa"]
                            break
                    elif origen_texto == "DF VIP":
                        # Modificado para filtrar solo mensajes que tengan marcas correctas en /propiedades
                        if op_data["origen"] == "PARTIDADNI":
                            if "MEXES" in texto_a_buscar or "PARTIDA" in texto_a_buscar:
                                op_encontrada = clave
                                placa_detectada = op_data["placa"]
                                break
                            else:
                                continue
                        elif op_data["origen"] in ["PARTIDA", "PARTIDAV"]:
                            # Aceptamos el mensaje si contiene MEXES o PARTIDA
                            if "MEXES" in texto_a_buscar or "PARTIDA" in texto_a_buscar:
                                op_encontrada = clave
                                placa_detectada = op_data["placa"]
                                break
                            else:
                                continue

                    elif origen_texto == "FRANCHESCO":
                        # 1. Filtro especial para búsquedas por DNI / Propiedades
                        if op_data["origen"] == "PARTIDADNI":
                            if any(k in texto_a_buscar for k in ["MEXES", "PARTIDA", "PROPIEDADES", "DNI"]):
                                op_encontrada = clave
                                placa_detectada = op_data["placa"]
                                break
                            else:
                                continue

                        # 2. Filtro expandido para consultas vehiculares (PLACA, TIVE, BOLETA, DENUNCIAS)
                        # Agregamos palabras clave de éxito y también de error para que no se quede callado
                        palabras_validas_franchesco = [
                            "MEXES", "HUGO", "BOLETA", "TIVE", "INFORMATIVA", 
                            "PROCESADO", "REGISTRO", "NO SE ENCONTRÓ", "NO SE ENCONTRO", 
                            "ERROR", "NO EXISTE", "SIN RESULTADOS"
                        ]

                        if any(palabra in texto_a_buscar for palabra in palabras_validas_franchesco):
                            if op_data["origen"] in ["PLACA", "TIVE", "BOLETA", "DENUNCIAS"]:
                                op_encontrada = clave
                                placa_detectada = op_data["placa"]
                                break
                            op_encontrada = clave
                            placa_detectada = op_data["placa"]
                            break
                        else:
                            continue

                    # --- FILTRO Y ASIGNACIÓN PARA EL GRUPO KIMICO ---
                    elif origen_texto == "KIMICO":
                        if texto_a_buscar.strip().startswith("/"):
                            continue

                        # Aceptamos cualquier reporte que contenga la placa de la operación
                        if op_data["origen"] in ["TIVE", "RQ", "BOLETA", "PLACA"]:
                            op_encontrada = clave
                            placa_detectada = op_data["placa"]
                            break
                        else:
                            continue

        if not op_encontrada: 
            return

        if event.message.media and event.message.document:
            nombre_original = "documento.pdf"
            for attr in event.message.document.attributes:
                if hasattr(attr, 'file_name') and attr.file_name:
                    nombre_original = attr.file_name
                    break

            if origen_texto == "NORTH DATA": 
                north_respondido_exito[op_encontrada] = True

            ruta = await event.message.download_media(file=nombre_original)

            # Detectamos si es DNI o Placa para armar un mejor diseño de mensaje
            tipo_identificador = "👤 DNI" if control_operaciones[op_encontrada]["origen"] == "PARTIDADNI" else "🏁 Placa/Partida"
            caption_personalizado = f"📄 <b>Resultado ({origen_texto}):</b>\n{tipo_identificador}: <code>{placa_detectada}</code>"

            with open(ruta, 'rb') as doc:
                bot.send_document(chat_id_hugo, doc, caption=caption_personalizado, parse_mode="HTML")

            if os.path.exists(ruta):
                try: os.remove(ruta)
                except: pass

            verificar_y_marcar_respuesta(op_encontrada, origen_texto)
            return

        elif event.message.media and event.message.photo and origen_texto in ["FRANCHESCO", "NORTH DATA"]:
            comando_origen = control_operaciones[op_encontrada]["origen"]
            caption_proveedor = event.message.message if event.message.message else ""

            # Filtro para omitir imágenes publicitarias en Franchesco si aplica
            if origen_texto == "FRANCHESCO" and comando_origen in ["TIVE", "BOLETA", "DENUNCIAS"]:
                print(f"🤫 Imagen publicitaria omitida en ráfaga para {placa_detectada}.")
                verificar_y_marcar_respuesta(op_encontrada, "FRANCHESCO")
                return

            palabras_carga_imagen = ["CONSULTANDO PLACA", "POR FAVOR ESPERA", "ESTAMOS PROCESANDO", "UN MOMENTO POR FAVOR"]
            if any(carga in caption_proveedor.upper() for carga in palabras_carga_imagen):
                print(f"⏳ [PROCESANDO] Se detectó pantalla de carga visual de {origen_texto} para {placa_detectada}...")
                return

            print(f"📸 ¡Reporte de imagen detectado para {placa_detectada} en {origen_texto}! Enviando...")
            ruta_img = await event.message.download_media(file=f"{placa_detectada}.jpg")

            try:
                msg_carga = control_operaciones[op_encontrada].get("msg_carga")
                if msg_carga:
                    try:
                        bot.delete_message(msg_carga.chat.id, msg_carga.message_id)
                    except Exception as e:
                        print(f"⚠️ No se pudo borrar el mensaje de carga: {e}")

                # Se envía ÚNICAMENTE la imagen limpia sin caption de texto adicional
                with open(ruta_img, 'rb') as foto_enviar:
                    bot.send_photo(chat_id_hugo, foto_enviar)
                print(f"✅ [ÉXITO] Imagen entregada para {placa_detectada} desde {origen_texto}")

            except Exception as e:
                print(f"❌ Error en el flujo de envío de foto: {e}")

            # Si es una consulta de imagen directa (/placa), marcamos la operación como finalizada
            if comando_origen == "PLACA":
                verificar_y_marcar_respuesta(op_encontrada, origen_texto)

            if os.path.exists(ruta_img):
                try: os.remove(ruta_img)
                except: pass
            return

        elif event.message.text:
            # 🚀 PARSER DIRECTO LÍNEA POR LÍNEA PARA KIMICO (CON FECHA PROP)
            if origen_texto == "KIMICO":
                texto_raw = event.message.text
                
                # Ignoramos avisos o confirmaciones intermedias de Kimico
                if "CONSULTA DE PLACA" not in texto_raw.upper() and "PROPIETARIO" not in texto_raw.upper():
                    return

                val_placa = placa_detectada
                val_oficina = "NO REGISTRA"
                val_partida = "NO REGISTRA"
                val_nombre = "NO REGISTRA"
                val_doc = "NO REGISTRA"
                val_fecha_prop = "NO REGISTRA"

                # Recorremos cada línea limpiando formatos invisibles de Telegram
                for linea in texto_raw.split("\n"):
                    linea_limpia = linea.replace("`", "").replace("*", "").replace("_", "").strip()
                    
                    if ":" in linea_limpia:
                        clave, valor = linea_limpia.split(":", 1)
                        clave_u = clave.upper().strip()
                        valor_txt = valor.strip()

                        if not valor_txt:
                            continue

                        if clave_u == "PLACA":
                            val_placa = valor_txt
                        elif clave_u == "OFICINA":
                            val_oficina = valor_txt
                        elif "PARTIDA" in clave_u:
                            val_partida = valor_txt
                        elif clave_u == "NOMBRE":
                            val_nombre = valor_txt
                        elif clave_u == "DOC":
                            val_doc = valor_txt
                        elif "FECHA PROP" in clave_u:
                            val_fecha_prop = valor_txt

                mensaje_kimico = (
                    f"📢 <b>Respuesta de [KIMICO]:</b>\n\n"
                    f"<b>PLACA :</b> <code>{val_placa}</code>\n"
                    f"<b>OFICINA :</b> {val_oficina}\n"
                    f"<b>N° PARTIDA :</b> <code>{val_partida}</code>\n"
                    f"<b>NOMBRE :</b> {val_nombre}\n"
                    f"<b>DOC :</b> {val_doc}\n"
                    f"<b>FECHA PROP :</b> <code>{val_fecha_prop}</code>"
                )
                bot.send_message(chat_id_hugo, mensaje_kimico, parse_mode="HTML")
                verificar_y_marcar_respuesta(op_encontrada, "KIMICO")
                return

            texto_grupo = event.message.text.upper()

            if texto_grupo.startswith(('/TIVE', '/TIV', '/PLA', '/PARTI', '/BOI', '/BOLI', '/BOLETA', '/DENPLA', '/DENUNV', '/PROP')) and len(texto_grupo) < 15 and not "NO SE" in texto_grupo: 
                return

            if texto_grupo.strip() == "CMDS" or (texto_grupo.startswith('/') and len(texto_grupo) < 7): return

            if origen_texto == "FRANCHESCO" and "ANTI-SPAM ACTIVADO" in texto_grupo:
                print(f"⚠️ [FRANCHESCO] Detectado Anti-Spam activo para la operación {op_encontrada}.")
                bot.send_message(
                    chat_id_hugo, 
                    f"⏳ <b>Alerta [{origen_texto}]:</b>\n\n⚠️ Tienes el Anti-Spam activado en este proveedor. Espera unos segundos.",
                    parse_mode="HTML"
                )
                verificar_y_marcar_respuesta(op_encontrada, "FRANCHESCO")
                return

            palabras_carga = [
                "BUSCANDO", "PROCESANDO", "ESPERE", "CONSULTANDO", "RECIBIDO", 
                "UN MOMENTO", "BUSQUEDA ACTIVADA", "SOLICITUD RECIBIDA", "CRÉDITOS RESTANTES",
                "OBTENIENDO LA TIVE", "OBTENIENDO", "𝐄𝐬𝐭𝐚𝐦𝐨𝐬 𝐩𝐫𝐨𝐜𝐞𝐬𝐚𝐧𝐝𝐨", "𝐔𝐧 𝐦ο𝐦𝐞𝐧𝐭ο",
                "OBTENIENDO LA TIVE DE LA"
            ]
            if any(carga in texto_grupo for carga in palabras_carga): return

            comando_origen = control_operaciones[op_encontrada]["origen"]

            if origen_texto == "FRANCHESCO":
                if "NO SE ENCONTRÓ" in texto_grupo or "NO SE ENCONTRO" in texto_grupo or "ERROR" in texto_grupo:
                    print(f"❌ [FRANCHESCO] Reportó error en texto plano para {placa_detectada}.")

                    if comando_origen in ["PLACA", "DENUNCIAS"]:
                        msg_carga = control_operaciones[op_encontrada].get("msg_carga")
                        if msg_carga:
                            try: bot.delete_message(msg_carga.chat.id, msg_carga.message_id)
                            except: pass

                    bot.send_message(chat_id_hugo, f"📢 **Respuesta de [{origen_texto}]:**\n🏁 Placa/Partida: `{placa_detectada}`\n\n❌ No se encontró información para los datos ingresados.")
                    verificar_y_marcar_respuesta(op_encontrada, origen_texto)
                    return

            if origen_texto == "DF VIP":
                es_error_df = "NO SE ENCONTRÓ" in texto_grupo or "NO SE ENCONTRO" in texto_grupo or "ERROR" in texto_grupo or "NO EXISTE" in texto_grupo

                if es_error_df:
                    print(f"❌ [DF VIP] Reportó falta de datos para {placa_detectada}.")

                    # SI FALLÓ EL TIVE, CORREMOS LA LOGICA DE RETARDO Y ADVERTENCIA
                    if comando_origen == "TIVE":
                        print(f"🔄 [DF VIP CONTROLADO] TIVE no encontrada. Avisando y programando /partidav en 15s...")

                        # 1. Enviar el mensaje inmediato al usuario avisando que no tenía TIVE con parseo HTML activo
                        bot.send_message(
                            chat_id_hugo, 
                            f"⚠️ <b>Aviso [DF VIP]:</b>\n🏁 Placa: <code>{placa_detectada}</code>\n\n❌ No se encontró la TIVE. Esperando 15 segundos para consultar Partida...",
                            parse_mode="HTML"
                        )

                        # 2. Definimos una pequeña subtarea asíncrona para esperar y disparar el comando
                        async def ejecutar_respaldo_partida(id_grupo, placa, clave_op):
                            await asyncio.sleep(15)
                            global control_operaciones
                            if clave_op in control_operaciones:
                                print(f"🚀 [DF VIP] Pasaron los 15s. Soltando comando: /partidav {placa}")
                                control_operaciones[clave_op]["origen"] = "PARTIDAV"
                                await client.send_message(id_grupo, f"/partidav {placa}")

                        # Lanzamos la espera en el loop principal para no bloquear el flujo del bot
                        asyncio.run_coroutine_threadsafe(ejecutar_respaldo_partida(id_df_vip, placa_detectada, op_encontrada), loop_principal)
                        return

                    # Si ya falló estando en PARTIDAV, DENUNCIAS o PARTIDADNI, cerramos la operación normalmente
                    if comando_origen in ["PARTIDAV", "DENUNCIAS", "PARTIDADNI"]:
                        msg_carga = control_operaciones[op_encontrada].get("msg_carga")
                        if msg_carga:
                            try: bot.delete_message(msg_carga.chat.id, msg_carga.message_id)
                            except: pass

                    bot.send_message(chat_id_hugo, f"⚠️ Resultado [{origen_texto}]:\n🏁 Placa: `{placa_detectada}`\n\n❌ No se encontró información o registros en este proveedor.")
                    verificar_y_marcar_respuesta(op_encontrada, origen_texto)
                    return

                elif comando_origen == "PARTIDAV":
                    # Si tiene marcas de que es el reporte final en texto plano, lo dejamos pasar
                    if "MEXES" in texto_grupo or "PARTIDA" in texto_grupo:
                        print(f"✅ [DF VIP] Detectado texto plano final de Partida para {placa_detectada}.")
                    else:
                        print(f"🤫 Texto plano intermedio de DF VIP ignorado para {placa_detectada}. Esperando el reporte...")
                        return

            if origen_texto == "NORTH DATA":
                es_error_north = (
                    "NO SE HAN ENCONTRADO DATOS" in texto_grupo or 
                    "NOT FOUND DATA" in texto_grupo or 
                    "NO SE ENCONTRÓ" in texto_grupo or
                    "NO SE ENCONTRO" in texto_grupo or
                    "NO SE HALLARON" in texto_grupo or
                    "ERROR" in texto_grupo or 
                    "NO EXISTE" in texto_grupo or
                    "NO CUENTA CON TIVE" in texto_grupo
                )

                if es_error_north:
                    print(f"❌ [NORTH DATA] Reportó falta de datos para {placa_detectada}. Reenviando alerta...")

                    texto_original = event.message.text

                    # Si el mensaje contiene explícitamente que no cuenta con TIVE, extraemos esa línea exacta
                    if "NO CUENTA CON TIVE" in texto_original.upper():
                        lineas = texto_original.split('\n')
                        reporte_recortado = ""
                        for linea in lineas:
                            if "NO CUENTA CON TIVE" in linea.upper():
                                # Preservamos la línea tal cual viene del proveedor original
                                reporte_recortado = linea.strip()
                                break
                        if not reporte_recortado:
                            reporte_recortado = "⚠️ El vehículo no cuenta con TIVE."
                    else:
                        # Comportamiento de recorte por defecto para otros errores de North Data
                        lineas = texto_original.split('\n')
                        lineas_limpias = []
                        for linea in lineas:
                            if "CONSULTADO POR" in linea.upper() or "CREDITOS" in linea.upper(): break
                            lineas_limpias.append(linea)
                        reporte_recortado = "\n".join(lineas_limpias).strip()

                    if not reporte_recortado: 
                        reporte_recortado = texto_original.strip()

                    bot.send_message(
                        chat_id_hugo, 
                        f"📢 <b>Respuesta de [{origen_texto}]:</b>\n🏁 Placa/Partida: <code>{placa_detectada}</code>\n\n{reporte_recortado}",
                        parse_mode="HTML"
                    )

                    if comando_origen == "TIVE" and not north_respondido_exito.get(op_encontrada):
                        print(f"⏱️ [NORTH DATA] Primer intento fallido en ráfaga /tive. Manteniendo operación viva para el reintento...")
                    else:
                        verificar_y_marcar_respuesta(op_encontrada, origen_texto)
                    return
                else:
                    print(f"🤫 Texto intermedio de North Data recibido para {placa_detectada}. Esperando...")
                    return

            texto_original = event.message.text
            lineas = texto_original.split('\n')
            lineas_limpias = []
            for linea in lineas:
                if "CONSULTADO POR" in linea.upper() or "CREDITOS" in linea.upper(): break

                linea_procesada = (linea.replace("`", "")
                                        .replace("**", "")
                                        .replace("__", "")
                                        .replace("_", "")
                                        .replace("[", "")
                                        .replace("]", "")
                                        .replace("*", ""))

                linea_procesada = re.sub(r'(=&gt;|&gt;|⇒|=>|->|➾)', ':', linea_procesada)

                for car in ['\\', '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
                    linea_procesada = linea_procesada.replace(car, f"\\{car}")

                linea_procesada = re.sub(r'(?<!\d)(\d+)(?!\d)', r'<code>\1</code>', linea_procesada)
                lineas_limpias.append(linea_procesada)

            reporte_recortado = "\n".join(lineas_limpias).strip()
            if not reporte_recortado: 
                reporte_recortado = texto_original.strip()

            try:
                markup_botones = None
                if event.message.reply_markup and hasattr(event.message.reply_markup, 'rows'):
                    markup_botones = InlineKeyboardMarkup()
                    for row in event.message.reply_markup.rows:
                        fila_botones = []
                        for button in row.buttons:
                            if hasattr(button, 'data'):
                                boton_data_hex = button.data.hex()
                                callback_compuesto = f"prov_{chat_actual_id}_{event.message.id}_{boton_data_hex}"

                                if len(callback_compuesto) <= 64:
                                    fila_botones.append(InlineKeyboardButton(text=button.text, callback_data=callback_compuesto))
                        if fila_botones:
                            markup_botones.add(*fila_botones)

                mensaje_html = f"📢 <b>Respuesta de [{origen_texto}]:</b>\n🏁 Placa/Partida: <code>{placa_detectada}</code>\n\n{reporte_recortado}"
                bot.send_message(
                    chat_id_hugo, 
                    mensaje_html,
                    parse_mode="HTML",
                    reply_markup=markup_botones
                )

                if markup_botones:
                    print(f"📥 [BOTONES DETECTADOS] Se clonaron los botones interactivos del proveedor {origen_texto} para {placa_detectada}.")
                    return 

            except Exception as e:
                print(f"⚠️ Error en HTML o mapeo de botones, aplicando respaldo seguro: {e}")
                bot.send_message(chat_id_hugo, f"📢 Respuesta de [{origen_texto}]:\n🏁 Placa/Partida: {placa_detectada}\n\n{texto_original}")

            verificar_y_marcar_respuesta(op_encontrada, origen_texto)

    print("🚀 [SISTEMA ULTRA-ESTABLE ONLINE] Extracción prioritaria activa sin OCR.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    print("Iniciando sistema multimotor seguro...")

    # 1. Lanzamos el bot de PyTelegramBotAPI (Telebot) en su propio hilo independiente
    threading.Thread(target=arrancar_bot_padre, daemon=True).start()

    # 2. Creamos y configuramos explícitamente el bucle asíncrono para el hilo principal (Evita el RuntimeError en Render)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # 3. Corremos la función principal asíncrona de Telethon
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot detenido por el usuario.")
    finally:
        loop.close()
