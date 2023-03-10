class Pedido:
    def __init__(self, id_u ,usuario, estado, fecha_e, fecha_c):
        self.id_u = id_u
        self.usuario = usuario
        self.estado = estado
        self.fecha_c = fecha_c
        self.fecha_e = fecha_e

    def toDbCollection(self):
        return{
            'Id_User':self.id_u,
            'usuario':self.usuario,
            'estado':self.estado,
            'fecha_creada':self.fecha_c,
            'fecha_entrega': self.fecha_e
        }