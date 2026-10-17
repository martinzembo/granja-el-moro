// URL del backend. Se arma a partir del host desde el que se abrió el
// panel (no se hardcodea "localhost"): si el admin abre el panel en el
// navegador de la misma compu que corre el backend, da lo mismo; pero si
// lo abre desde otro dispositivo apuntando a la IP de esa compu en la red
// de la granja (ej. http://192.168.1.50:5173), el backend se busca en esa
// misma IP, puerto 8000 — ver CLAUDE.md, sección Web.
export const apiBaseUrl = `http://${window.location.hostname}:8000`
