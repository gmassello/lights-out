# Pendiente — cierre Dark Factory (WeAreDevelopers × BAND)

Cierre: **lun 5 oct 2026, 23:59 PDT** (mar 6 oct 2026, 03:59 ART). Competencia:
<https://lablab.ai/ai-hackathons/wearedevelopers-hackathon> · Submission: <pendiente: inscripción + equipo> · PR: <no aplica>.

Etapas (de la página del evento y la participant guide): submissions hasta lun 5 oct 23:59 PDT, judging <not published>,
ganadores <not published>.

Estado del codigo en una linea: <N tests verdes, que esta hecho, que falta>.

---

## Superficies

| Superficie | Donde | Estado | Verificado |
|---|---|---|---|
| Repo y CI | `<owner>/<repo>` @ `<sha>` | | |
| Sitio | <URL> | | |
| Submission | <URL publica, no /edit> | | |
| Tarjeta en la galeria | <URL de la galeria> | | |
| PR upstream | #<n> | | |
| Segundo checkout | `~/<ruta>` rama `<rama>` | | |
| Video | `<id>` | | |

## Hechos duplicados

| Hecho | Valor real | Comando que lo produce | Copias |
|---|---|---|---|
| Cantidad de tests | | `uv run pytest -q \| tail -1` | |
| Archivos del PR | | `gh pr view <n> --json files --jq '.files\|length'` | |
| Version | | | |

## Lo que no cierra

Lo que no funciona, con el motivo. Esto es lo que evita prometer de mas en el formulario, y en una
competencia donde todos prometen, decirlo es diferencial.

- **<Cosa>** — <por que no cierra, y que haria falta para cerrarla>.

## No romper esto al volver

Las trampas del repo, para el que lo toque dentro de tres dias (que sos vos, sin contexto).

- `<script>` borra `<directorio gitignoreado>`: si se corre, se pierde <que>.
- `<archivo generado>` tiene que copiarse tambien a `<segundo lugar>`.
- `<test>` fija el output de `<comando>`: cambiar el formato obliga a reconciliarlo a mano.

## Fuera de mi control

No son tareas: son riesgos. Cada uno con su fallback.

- **Inscripción en lablab + Discord + equipo propio como admin** — sin los tres, *Submit Project* queda gris. Fallback: ninguno; hacerlo antes del lun 28 sep, no el último día.
- **Cuenta BAND y readiness check de Desktop** — depende del instalador y del plugin de BAND. Fallback: preguntar en el BAND Discord; un seat que no arranca en OpenCode pasa a Claude Code.
- **Cupo del modelo durante la corrida autónoma** — si un seat se queda sin cupo a mitad de etapa, no se puede intervenir. Fallback: lanzar la corrida al inicio de una ventana limpia, con el costo del toy ya medido.
- **Créditos Featherless** — primeros 1.000 inscriptos, promo por mail. Fallback: suscripción o API key propia.
- **Descarga de `room.json` desde Band console** — manual, sin comando del harness. Fallback: bajarlo apenas termina la corrida y volver a bajarlo al final.
- **Fechas de judging y de ganadores** — not published. Fallback: ninguno necesario para entregar.
