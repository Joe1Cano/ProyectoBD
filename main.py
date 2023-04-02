from flask import Flask, render_template, redirect, request, jsonify, url_for
import requests 
import numpy as np
import json
import mongo as dbase
from pedidos import Pedido
from bson.objectid import ObjectId
import datetime
import random
import bson

db=dbase.dbConnection()

app = Flask(__name__)
app.debug= True

@app.route('/')
def index():
    return render_template('usuarios/home.html')

@app.route("/cUser")
def cUser():
    return render_template('usuarios/create.html')

@app.route("/menu")
def menu():
    return render_template('main/menu.html')

@app.route("/return/<int:id>/<string:user>")
def exit(id,user):
    id_u=id
    return redirect(url_for('menuC', user=user, id_u = id_u))

@app.route("/exit/<string:user>/<int:id>")
def exitM(id,user):
    id_u=id
    return redirect(url_for('menuC', user=user, id_u = id_u))

@app.route("/pedido/<int:id>/")
def pedioC(id):
    datos = []
    pedidos = db['Pedidos']
    pedidoReceived = pedidos.find({'Id_User': str(id)})
    for i in pedidoReceived:
        datos.append(i['_id'])
        datos.append(i['Id_User'])
        datos.append(i['usuario'])
        datos.append(i['estado'])
        datos.append(i['fecha_creada'])
        datos.append(i['fecha_entrega'])
    def chunk_list(lst, chunk_size):
            for i in range(0, len(lst), chunk_size):
                yield lst[i:i + chunk_size]
        
    x = list(chunk_list(datos, 6))
    print(x)
    return render_template('cliente/pedido.html', data=x)

@app.route("/proC", methods=["post"])
def proC():
    datos = []
    id = request.form["idP"]
    url = "http://172.31.24.91:82/product_id/" + str(id)
    inv = requests.get(url)
    print(url)
    if inv.status_code == 200:
        inv = inv.json()
        for i in inv['data']:
            datos.append(i['product_id'])
            datos.append(i['name'])
            datos.append(i['price'])
            datos.append(i['quantity'])
            datos.append(i['url'])

    cant = int(request.form["quantity"])
    totalI=int(datos[3])

    newQ = totalI - cant
    print(newQ)
    
    _Nombre = datos[1]
    _Precio = datos[2]
    _Cantidad = newQ
    _Url = datos[4]
    id = datos[0]

    url = "http://172.31.24.91:82/product/"+ str(id)

    payload = json.dumps({
        "name": _Nombre,
        "price": _Precio,
        "quantity": _Cantidad,
        "url": _Url
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    id_u = request.form["idU"]
    id_product = id
    quantity = cant
    price = _Precio
    id_pedido=request.form["pedido"]
    total = request.form["total"]
    user = request.form["user"]

    url = "http://172.31.24.91:8018product"

    payload = json.dumps({
        "id_user": id_u,
        "id_product": id_product,
        "id_pedido": id_pedido,
        "quantity": quantity,
        "price": price,
        "total": total
    })
    print(payload)
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    if response.status_code == 200:
        return redirect(url_for('menuC', user=user, id_u=id_u))

@app.route("/proP", methods=["post"])
def proP():
    random_number = random.randint(1, 7)
    current_date = datetime.date.today()
    days_to_add = random_number
    new_date = current_date + datetime.timedelta(days=days_to_add)
    string_date = current_date.strftime('%Y-%m-%d')
    new_string_date = new_date.strftime('%Y-%m-%d')
    

    pedidos = db['Pedidos']
    _Usuario = request.form["txtUsuario"]
    _Precio = request.form["precio"]
    _Estado = "Preparando"
    _FechaC = string_date
    _FechaE = new_string_date
    _idU = request.form["idU"]
    _Cantidad = request.form["productQuantity"]
    _Total = request.form["productTotal"]
    _idP = request.form["idP"]

    if _Usuario and _Estado and _FechaC and _FechaE:
        order = Pedido(_idU, _Usuario, _Estado, _FechaE, _FechaC)
        result = pedidos.insert_one(order.toDbCollection())
        idV= result.inserted_id
        response = jsonify({
            'id_user': _idU,
            'usuario': _Usuario,
            'estado': _Estado,
            'fecha_creda': _FechaC,
            'fecha_entrega': _FechaE
        })
        return render_template('cliente/procesar.html', user=_Usuario, idP = _idP, id_u=_idU, idV=idV,cant=_Cantidad, prec=_Precio, total=_Total)
    else:
        return notFound()

@app.route("/subtotal", methods=['POST'])
def subT():
    _idP = request.form["id"]
    _nomP = request.form["name"]
    _precio = request.form["price"]
    _cantidad = request.form["quantity"]
    _user = request.form["user"]
    _idU = request.form["id_u"]

    prodct = []
    prodct.append(_idP)
    prodct.append(_nomP)
    prodct.append(_precio)
    prodct.append(_cantidad)
    prodct.append(_user)
    prodct.append(_idU)

    print(prodct)

    return render_template('cliente/compra.html', data=prodct)

@app.route("/menuC")
def menuC():
    invent=[]
    url = 'http://172.31.24.91:82'
    inv = requests.get(url)
    if inv.status_code == 200:
        inv = inv.json()
        for i in inv['data']:
            invent.append(i['product_id'])
            invent.append(i['name'])
            invent.append(i['price'])
            invent.append(i['quantity'])
            invent.append(i['url'])

        def chunk_list(lst, chunk_size):
            for i in range(0, len(lst), chunk_size):
                yield lst[i:i + chunk_size]
        
        x = list(chunk_list(invent, 5))
        user = request.args.get('user')
        id_u = request.args.get('id_u')

        def remove_subarray(array, value):
            for i, element in enumerate(array):
                if element == value:
                    del array[i]
                    return True
                elif isinstance(element, list):
                    if remove_subarray(element, value):
                        del array[i]
                        return True
            return False
        remove_subarray(x, 0)

    return render_template('cliente/home.html', inv=x, user=user, id_u = id_u)

@app.route("/validate", methods=['POST'])
def validar():
    _Correo = request.form["email"]
    _Password = request.form["password"]

    url = 'http://172.31.24.91:801'
    invent=[]
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        for i in data['data']:
            invent.append(i['usuario_id'])
            invent.append(i['name'])
            invent.append(i['l_name'])
            invent.append(i['correo'])
            invent.append(i['password'])
            invent.append(i['tipo'])

        def chunk_list(lst, chunk_size):
            for i in range(0, len(lst), chunk_size):
                yield lst[i:i + chunk_size]
        
        x = list(chunk_list(invent, 6))
        value = _Correo
        array = x

        def search_array(array, value):
            for element in array:
                if element == value:
                    return array
                elif isinstance(element, list):
                    subarray = search_array(element, value)
                    if subarray:
                        return subarray
            return None

        subarray = search_array(array, value)
        if subarray:
            if(_Correo == subarray[3] and _Password == subarray[4]):
                if(subarray[5] == 0):
                    user = subarray[1]
                    id_u = subarray[0]
                    return redirect(url_for('menuC', user=user, id_u=id_u))
                elif(subarray[5] == 1):
                    return redirect('/menu')
            else:
                return redirect('/')
        else:
            print("Value not found.")
            return redirect('/')
    else:
        print(f'Request failed with status code {response.status_code}')

@app.route("/saveU", methods=['POST'])
def saveU():
    _Nombre = request.form["name"]
    _Apellido = request.form["l_name"]
    _Correo = request.form["email"]
    _Contrasena = request.form["password"]
    _Tipo = request.form["tipo"]

    url = "http://172.31.24.91:801/product"

    payload = json.dumps({
        "name": _Nombre,
        "l_name": _Apellido,
        "correo": _Correo,
        "password": _Contrasena,
        "tipo": _Tipo
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    if response.status_code == 200:
        return redirect('/')

@app.route('/inv')
def inv():
    invent=[]
    url = 'http://172.31.24.91:82'
    inv = requests.get(url)
    if inv.status_code == 200:
        inv = inv.json()
        for i in inv['data']:
            invent.append(i['product_id'])
            invent.append(i['name'])
            invent.append(i['price'])
            invent.append(i['quantity'])
            invent.append(i['url'])

        def chunk_list(lst, chunk_size):
            for i in range(0, len(lst), chunk_size):
                yield lst[i:i + chunk_size]
        
        x = list(chunk_list(invent, 5))

        return render_template('main/main.html', inv=x)

@app.route('/delete/<int:id>')
def delete(id):
    url = 'http://172.31.24.91:82/product_id/'
    #return str(id)
    print(url)
    inv = requests.request("DELETE", url+str(id))
    if inv.status_code == 200:
        return redirect('/inv')

@app.route('/create/')
def create():
    return render_template('main/create.html')

@app.route("/guardar", methods=['POST'])
def store():
    _Nombre = request.form["txtNombre"]
    _Precio = request.form["txtPrecio"]
    _Cantidad = request.form["txtCantidad"]
    _Url = request.form["txtUrl"]

    url = "http://172.31.24.91:82/product"

    payload = json.dumps({
        "name": _Nombre,
        "price": _Precio,
        "quantity": _Cantidad,
        "url" : _Url
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    if response.status_code == 200:
        return redirect('/inv')

@app.route('/edit/<int:id>')
def edit(id):
    datos = []
    url = "http://172.31.24.91:82/product_id/" + str(id)
    inv = requests.get(url)
    if inv.status_code == 200:
        inv = inv.json()
        for i in inv['data']:
            datos.append(i['product_id'])
            datos.append(i['name'])
            datos.append(i['price'])
            datos.append(i['quantity'])
            datos.append(i['url'])
    
    return render_template('main/edit.html', datos=datos)

@app.route("/update", methods=['post'])
def update():
    _Nombre = request.form["txtNombre"]
    _Precio = request.form["txtPrecio"]
    _Cantidad = request.form["txtCantidad"]
    _Url = request.form["txtUrl"]
    id = request.form["txtId"]

    url = "http://172.31.24.91:82/product/"+ id

    payload = json.dumps({
        "name": _Nombre,
        "price": _Precio,
        "quantity": _Cantidad,
        "url": _Url
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    print(response.text)
    if response.status_code == 200:
        return redirect('/inv')

@app.route("/mongo")
def indexM():
    pedido=[]
    pedidos = db['Pedidos']
    pedidoReceived = pedidos.find()
    for i in pedidoReceived:
        pedido.append(i['_id'])
        pedido.append(i['Id_User'])
        pedido.append(i['usuario'])
        pedido.append(i['estado'])
        pedido.append(i['fecha_creada'])
        pedido.append(i['fecha_entrega'])

    def chunk_list(lst, chunk_size):
            for i in range(0, len(lst), chunk_size):
                yield lst[i:i + chunk_size]
        
    x = list(chunk_list(pedido, 6))
    return render_template('mongo/index.html', pedido=x)

@app.route('/mongo/create')
def crear():
    return render_template('mongo/create.html')

@app.route("/mongo/editar/<string:id>")
def func(id):
    datos = []
    pedidos = db['Pedidos']
    pedidoReceived = pedidos.find({'_id': ObjectId(id)})
    for i in pedidoReceived:
        datos.append(i['_id'])
        datos.append(i['Id_User'])
        datos.append(i['usuario'])
        datos.append(i['estado'])
        datos.append(i['fecha_creada'])
        datos.append(i['fecha_entrega'])
    return render_template('mongo/edit.html', data=datos)

@app.route("/mongo/pedido", methods=['POST'])
def saveM():
    pedidos = db['Pedidos']
    _Usuario = request.form["txtUsuario"]
    _idU = request.form["idU"]
    _Estado = request.form["estado"]
    _FechaC = request.form["fechaC"]
    _FechaE = request.form["fechaE"]

    if _Usuario and _Estado and _FechaC and _FechaE and _idU:
        order = Pedido(_idU,_Usuario, _Estado, _FechaE, _FechaC)
        pedidos.insert_one(order.toDbCollection())
        
        response = jsonify({
            'id_user': _idU,
            'usuario': _Usuario,
            'estado': _Estado,
            'fecha_creda': _FechaC,
            'fecha_entrega': _FechaE
        })
        return redirect(url_for('indexM'))
    else:
        return notFound()

@app.route("/mongo/delete/<string:id>")
def borrar(id):
    pedidos = db["Pedidos"]
    pedidos.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('indexM'))


@app.route("/mongo/edit", methods=['POST'])
def editarM():
    pedidos = db['Pedidos']
    _Usuario = request.form["txtUsuario"]
    _idU = request.form["idU"]
    _Estado = request.form["estado"]
    _FechaC = request.form["fechaC"]
    _FechaE = request.form["fechaE"]
    id = request.form["txtId"]

    if _Usuario and _Estado and _FechaC and _FechaE:
        pedidos.update_one({'_id': ObjectId(id)}, {'$set' : {'id_user':_idU, 'usuario': _Usuario, 'estado': _Estado, 'fecha_creada': _FechaC, 'fecha_entrega': _FechaE} })
        response = jsonify({'message':"producto"+id+"fue modificado"})
        return redirect(url_for('indexM'))
    else:
        return notFound()


app.run(port=3380, host="0.0.0.0")

@app.errorhandler(404)
def notFound(erro=None):
    message={
        'message': 'Not found' + request.url,
        'status': '404 Not Found'
    }
    response = jsonify(message)
    response.status_code = 404
    return response