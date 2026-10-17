# Despliegue en la notebook de la granja

Guía paso a paso para dejar el sistema corriendo en la notebook que va a
quedar prendida en la granja, en vez de en una PC de desarrollo. Pensada
para seguirla desde cero en una notebook Windows sin nada instalado.

Lo que va a correr ahí:
- **Backend** (FastAPI + PostgreSQL)
- **Panel web** (`web/`, build de producción — lo usa el administrador)

El APK del granjero **no corre acá** — corre en su celular. Lo único que
hace falta es compilarlo apuntando a esta notebook (último paso de esta
guía).

Si estás arrancando esto con una sesión de Claude Code nueva en la
notebook (no la misma sesión que hizo el resto del proyecto), decile que
lea este archivo entero antes de tocar nada — tiene todo el contexto que
necesita para seguir sin redescubrir el proyecto.

## 1. Instalar lo necesario

- **Git**: https://git-scm.com/download/win
- **Python 3.11+**: https://www.python.org/downloads/ — tildar "Add
  python.exe to PATH" en el instalador
- **Node.js LTS**: https://nodejs.org/
- **PostgreSQL 17**: https://www.postgresql.org/download/windows/ — anotar
  la contraseña que le pongas al usuario `postgres` durante la instalación,
  la vas a necesitar en el paso 3

## 2. Traer el proyecto

```bash
git clone https://github.com/martinzembo/granja-el-moro.git
cd granja-el-moro
```

## 3. Backend

Seguir [backend/README.md](../backend/README.md) tal cual (setup del venv,
`.env`, crear la base, migraciones, sembrar estándares, crear el admin).
Un par de cosas puntuales para esta notebook, no para desarrollo:

- En `backend/.env`, `DATABASE_URL` usa la contraseña de Postgres que
  pusiste en el paso 1.
- Generá una `SECRET_KEY` nueva y propia para esta instalación (no
  reutilices la de la PC de desarrollo) — el comando para generarla está en
  el README.
- El admin que crees acá con `crear_admin` es el que va a usar el
  administrador real de la granja día a día. Contraseña de verdad, no una
  de prueba.

## 4. Averiguar y fijar la IP de esta notebook

```powershell
ipconfig
```

Buscar la "Dirección IPv4" de la placa de red conectada al WiFi de la
granja (algo como `192.168.1.50`). **Importante:** si no se fija, el router
se la puede cambiar en cualquier momento y todo deja de funcionar sin
avisar. Entrar a la configuración del router (típicamente
`192.168.1.1` o `192.168.0.1` en el navegador) y buscar la sección de
**reserva de IP / DHCP reservation**, asociando esa IP a la dirección MAC
de la placa de WiFi de la notebook (la da `ipconfig /all`, campo "Dirección
física"). Cada router tiene una pantalla distinta para esto — si no se
encuentra, buscar "reserva DHCP" + la marca del router.

De acá en más, en esta guía, **`<IP-NOTEBOOK>`** es esa dirección fija.

## 5. Abrir el firewall de Windows

Por defecto, Windows bloquea conexiones entrantes a los puertos que van a
usar el backend y el panel. Ejecutar en PowerShell **como administrador**:

```powershell
New-NetFirewallRule -DisplayName "Granja El Moro - Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Granja El Moro - Panel web" -Direction Inbound -LocalPort 4173 -Protocol TCP -Action Allow
```

## 6. Correr el backend escuchando en la red (no solo localhost)

```bash
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

`--host 0.0.0.0` es la diferencia con el modo de desarrollo: sin esto, solo
la propia notebook podría conectarse, nadie más en la red de la granja.

Probar desde otro dispositivo en la misma red (el celular, por ejemplo,
abriendo `http://<IP-NOTEBOOK>:8000/health` en el navegador) que responda
`{"status":"ok"}`.

## 7. Build de producción del panel web y servirlo

```bash
cd web
npm install
npm run build
npm run preview -- --host 0.0.0.0 --port 4173
```

`npm run preview` sirve el build de `dist/` (el mismo que se generó con
`npm run build`) en vez del servidor de desarrollo — es el modo pensado
para esto, no `npm run dev`.

El administrador entra desde cualquier navegador de la red de la granja a
`http://<IP-NOTEBOOK>:4173`.

## 8. Que quede corriendo solo (sin dejar dos ventanas de terminal abiertas)

Para no depender de dejar las terminales de los pasos 6 y 7 abiertas a
mano, armar dos Tareas Programadas de Windows (`Programador de tareas` en
el menú inicio) que:

- Se disparen "Al iniciar sesión" (o "Al iniciar el sistema")
- Ejecuten cada comando de los pasos 6 y 7 respectivamente (acción
  "Iniciar un programa", apuntando a `python.exe`/`npm.cmd` con los
  argumentos correspondientes y el "Iniciar en" apuntando a la carpeta
  `backend`/`web`)

Así, si la notebook se reinicia (corte de luz, actualización de Windows),
el sistema vuelve solo sin que nadie tenga que acordarse de nada.

## 9. Backup de la base de datos

Sin esto, si la notebook falla, se pierde todo el historial de crianzas.
Programar (otra Tarea Programada, corriendo de noche) algo como:

```powershell
pg_dump -U postgres elmoro > "C:\Backups\elmoro-$(Get-Date -Format yyyyMMdd).sql"
```

apuntando `C:\Backups` a una carpeta sincronizada con Google Drive/Dropbox
(si hay cuenta disponible en esa notebook), para que el backup no dependa
del mismo disco que falló.

## 10. Compilar el APK real para el granjero

El APK que se usó para probar apunta a `localhost` (necesita `adb reverse`
y el celular por USB). El que va a usar el granjero en la granja, con su
celular conectado por WiFi, tiene que apuntar a esta notebook:

```bash
cd mobile
flutter build apk --release --dart-define=API_BASE_URL=http://<IP-NOTEBOOK>:8000
```

El APK queda en `mobile/build/app/outputs/flutter-apk/app-release.apk` —
pasarlo al celular del granjero (por cable, WhatsApp, lo que sea más fácil)
e instalarlo ahí. El granjero necesita tener el WiFi de la granja activo
para que la app funcione (ver la nota sobre cobertura WiFi en los galpones
que ya se charló para esta decisión).

## 11. (Opcional, para más adelante) Acceso remoto sin estar en el WiFi de la granja

Si en algún momento el administrador quiere revisar el panel desde afuera
de la granja (viajando, en el pueblo), instalar [Tailscale](https://tailscale.com)
en la notebook y en los celulares — conecta todos los dispositivos como si
estuvieran en la misma red local, sin abrir puertos del router a
internet directamente (que sí sería un riesgo real). Queda fuera del
alcance de esta guía porque no es necesario para el uso diario dentro de
la granja.

## Checklist final

- [ ] Backend responde en `http://<IP-NOTEBOOK>:8000/health` desde otro
      dispositivo de la red
- [ ] Panel web abre en `http://<IP-NOTEBOOK>:4173` desde otro dispositivo
- [ ] Login del administrador real funciona en el panel
- [ ] APK compilado con `--dart-define` instalado en el celular del
      granjero, y la carga diaria funciona por WiFi (sin USB, sin `adb reverse`)
- [ ] IP de la notebook reservada en el router
- [ ] Backend y panel arrancan solos si la notebook se reinicia
- [ ] Backup de la base programado
