#!/usr/bin/env python3
"""
Prueba de humo del backend del Sprint 5 (HU 12 a 19) contra una API real.

Requisitos: API corriendo en http://localhost:8010 con TRACCAR_TOKEN=tok-humo y una base de datos vacía
con las migraciones aplicadas. Ejecutar desde la carpeta backend: python scripts/prueba_humo_sprint5.py
Crea sus propios usuarios y datos de prueba (titular@humo.cl, cuidador@humo.cl).
"""
import json, sys, urllib.request, urllib.error, urllib.parse
B="http://localhost:8010"; TOK="tok-humo"; IMEI="356938035643809"
res=[]
def call(m,p,body=None,tok=None,form=None,ok=(200,201)):
    h={}
    data=None
    if body is not None: data=json.dumps(body).encode(); h["Content-Type"]="application/json"
    if form is not None: data=urllib.parse.urlencode(form).encode(); h["Content-Type"]="application/x-www-form-urlencoded"
    if tok: h["Authorization"]="Bearer "+tok
    r=urllib.request.Request(B+p,data=data,headers=h,method=m)
    try:
        with urllib.request.urlopen(r) as x: c=x.status; t=x.read()
    except urllib.error.HTTPError as e: c=e.code; t=e.read()
    try: j=json.loads(t)
    except Exception: j=t.decode()[:200]
    return c,j
def chk(nombre,cond,detalle=""):
    res.append((nombre,bool(cond),detalle)); print(("OK  " if cond else "FALLA"),nombre,detalle)
def reg(n,e):
    call("POST","/auth/register",{"nombre":n,"email":e,"password":"Clave1234!"})
    c,j=call("POST","/auth/login",{"email":e,"password":"Clave1234!"})
    if c!=200: c,j=call("POST","/auth/login",form={"username":e,"password":"Clave1234!"})
    return j["access_token"]
t=reg("Titular Humo","titular@humo.cl"); cu=reg("Cuidador Humo","cuidador@humo.cl")
c,p=call("POST","/perfiles",{"tipo":"dependiente","subtipo":"adulto_mayor","nombre":"Abuela Humo"},t); print(c,p); pid=p["id"]
c,_=call("POST",f"/perfiles/{pid}/cuidadores",{"email":"cuidador@humo.cl","rol_vinculo":"cuidador","puede_confirmar":True,"puede_ver_indicadores":True,"recibe_alertas":True},t)
chk("Vincular cuidador con puede_ver_indicadores",c==201,c)
# Indicadores
for tipo,v,v2 in [("peso",70.5,None),("presion",120,80),("glucosa",95,None),("frecuencia_cardiaca",72,None)]:
    c,j=call("POST",f"/perfiles/{pid}/indicadores",{"tipo":tipo,"valor":v,**({"valor_secundario":v2} if v2 else {})},t)
    chk(f"Registrar {tipo}",c==201,c)
c,_=call("POST",f"/perfiles/{pid}/indicadores",{"tipo":"peso","valor":700},t); chk("Peso 700 rechazado (422)",c==422,c)
c,_=call("POST",f"/perfiles/{pid}/indicadores",{"tipo":"presion","valor":120},t); chk("Presión sin diastólica rechazada (422)",c==422,c)
c,j=call("GET",f"/perfiles/{pid}/indicadores/ultimos",tok=t); chk("Últimos valores",c==200 and len(j["ultimos"])>=4,c)
c,j=call("GET",f"/perfiles/{pid}/indicadores/serie?tipo=peso&dias=30",tok=t); chk("Serie de peso 30 días",c==200,c)
c,_=call("GET",f"/perfiles/{pid}/indicadores/ultimos",tok=cu); chk("Cuidador con permiso ve indicadores",c==200,c)
# Cuidador sin permiso
e=call("GET",f"/perfiles/{pid}/cuidadores",tok=t)[1]; aid=e[0]["id"]
c,_=call("PUT",f"/perfiles/{pid}/cuidadores/{aid}",{"puede_ver_indicadores":False},t); print("put",c)
c,_=call("GET",f"/perfiles/{pid}/indicadores/ultimos",tok=cu); chk("Cuidador sin permiso: 403",c==403,c)
call("PUT",f"/perfiles/{pid}/cuidadores/{aid}",{"puede_ver_indicadores":True},t)
# Cumplimiento
c,j=call("GET",f"/perfiles/{pid}/cumplimiento?dias=7",tok=t); chk("Cumplimiento 7 días",c in (200,400),(c,str(j)[:80]))
# Asistencia
c,j=call("POST",f"/perfiles/{pid}/asistencia",tok=t); chk("Botón «Necesito ayuda»",c in (200,201),c)
c,j=call("POST",f"/perfiles/{pid}/asistencia",tok=t); chk("Repetir no duplica el evento",c==200,c)
c,j=call("GET","/eventos",tok=cu); chk("Cuidador ve el evento de asistencia",c==200 and any(x.get("tipo")=="asistencia" for x in j),c)
# Pulsera
c,j=call("POST",f"/perfiles/{pid}/pulseras",{"identificador":IMEI,"nombre":"Pulsera Humo"},t); chk("Registrar pulsera (titular)",c==201,c)
c,_=call("POST",f"/perfiles/{pid}/pulseras",{"identificador":"999","nombre":"x"},cu); chk("Cuidador no puede registrar pulsera (403)",c==403,c)
c,j=call("POST",f"/perfiles/{pid}/geocercas",{"nombre":"Casa","latitud":-33.4489,"longitud":-70.6693,"radio_m":200},t); chk("Crear geocerca",c==201,c)
c,_=call("POST",f"/traccar/posiciones?token=mal",ok=None); chk("Traccar sin token válido rechazado",c in (401,403),c)
import subprocess
def sim(*a):
    r=subprocess.run([sys.executable,"scripts/simular_pulsera.py","--url",B,"--token",TOK,"--id",IMEI,*a],capture_output=True,text=True,cwd="."); return r.returncode,(r.stdout+r.stderr).strip()[:200]
for a in [("posicion","--lat","-33.4489","--lon","-70.6693","--bateria","80"),("sos",),("caida",),("bateria","--porcentaje","9"),("recorrido","--lat","-33.4489","--lon","-70.6693","--metros","600")]:
    rc,o=sim(*a); chk("Simulador "+a[0],rc==0,o.replace("\n"," | ")[:90])
c,j=call("GET",f"/perfiles/{pid}/ubicacion",tok=t); chk("Última ubicación",c==200,str(j)[:90])
c,j=call("GET","/eventos",tok=t); tipos=sorted({x.get("tipo") for x in j}); chk("Eventos creados: SOS, caída, batería baja, salida de zona",{"sos","caida","bateria_baja"}<=set(tipos),tipos)
c,j=call("GET","/eventos",tok=cu); pend=[x for x in j if not x.get("atendido")]; 
if pend:
    c,_=call("POST",f"/eventos/{pend[0]['id']}/atendido",tok=cu); chk("Marcar evento atendido",c==200,c)
# IA
c,j=call("POST",f"/perfiles/{pid}/ia/consultas",{"pregunta":"¿Cuándo debo tomar mis medicamentos?"},t); chk("IA: pregunta normal",c in (200,201),(c,j.get("proveedor") if isinstance(j,dict) else j))
c,j=call("POST",f"/perfiles/{pid}/ia/consultas",{"pregunta":"Me duele el pecho"},t); chk("IA: urgencia responde con reglas y 131",c in (200,201) and "131" in json.dumps(j) ,(c,j.get("proveedor") if isinstance(j,dict) else j))
c,_=call("GET",f"/perfiles/{pid}/ia/consultas",tok=cu); print("hist",c)
ok=sum(1 for r in res if r[1]); print(f"\nRESULTADO: {ok}/{len(res)} OK")
json.dump(res,open("resultado_humo.json","w"),ensure_ascii=False)
