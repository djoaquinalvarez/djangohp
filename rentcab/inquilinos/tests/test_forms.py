import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase

from inquilinos.forms import CrearHuespedForm, RegResForm
from inquilinos.models import Cab, Estado, Huesped, Rango, Reserva


def get_a_cab():
    cab = Cab(
        nombre="cab_slug",
        cantHabitaciones=2,
        costoPorAdulto=500.0,
        costoPorMenor=200.0,
        cantMaxPersonas=6,
    )
    cab.save()
    return cab


def get_a_huesped(user):
    huesped = Huesped(
        usuario=user,
        nombre="nombre_test",
        apellido="apellido_test",
        telefono="3534267889",
    )

    huesped.save()
    return huesped


def crear_reserva(cab, user, fechaDesde, fechaHasta, cantAdultos=2, cantMenores=2):

    huesped = get_a_huesped(user)

    datos_reserva = {
        "fechaDesde": fechaDesde,
        "fechaHasta": fechaHasta,
        "cantAdultos": cantAdultos,
        "cantMenores": cantMenores,
        "huesped": huesped,
    }

    reserva = cab.crear_reserva(datos_reserva)

    return reserva


class RegistrarReservaFormTest(TestCase):
    def setUp(self):
        # Creación de un usuario para testeo
        self.user = get_user_model().objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK", email="test@test.com"
        )
        self.user.save()

        # creación de una cabaña
        test_cab = Cab(
            nombre="cab_test",
            cantHabitaciones=2,
            costoPorAdulto=500.0,
            costoPorMenor=200.0,
            cantMaxPersonas=6,
        )
        test_cab.save()

        # creación de un rango y una reserva
        test_rango = Rango(
            fechaDesde=datetime.date.today() - datetime.timedelta(weeks=2),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=2),
        )
        reserva = Reserva(
            fechaDesde=datetime.date.today(),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=1),
            cantAdultos=1,
        )
        reserva.save()
        test_rango.save()
        # creación del grupo con el que se manejan los permisos de la vista
        group = Group(name="huesped")
        group.save()
        # se agrega el permiso al grupo
        permission = Permission.objects.get(codename="puede_registrar_reserva")
        permission.save()
        group.permissions.add(permission)

        PteConf = Estado(nombre="Pte Confirmacion")
        PteConf.save()

    # tests para la fechaDesde
    def test_fecha_desde_antes_de_hoy(self):
        """Testea que no sea exitosa la carga de una reserva con la fecha de ingreso menor
        a la fecha actual."""
        cab = get_a_cab()

        rango = Rango(
            fechaDesde=datetime.date.today(),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=6),
            cab=cab,
        )

        rango.save()

        fechaDesdeHasta = (
            (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d/%m/%Y")
            + " - "
            + (datetime.date.today() + datetime.timedelta(weeks=4)).strftime("%d/%m/%Y")
        )

        cab_slug = "cab_slug"

        form = RegResForm(
            data={
                "fechaDesdeHasta": fechaDesdeHasta,
                "cab_slug": cab_slug,
                "cantAdultos": 2,
                "cantMenores": 2,
            }
        )
        self.assertFalse(form.is_valid())

    def test_fecha_desde_igual_a_hoy(self):
        """Testea que sea exitosa la carga de una reserva con la fecha de ingreso
        igual a la fecha actual."""
        cab = get_a_cab()
        rango = Rango(
            fechaDesde=datetime.date.today(),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=6),
            cab=cab,
        )

        rango.save()
        fechaDesdeHasta = (
            (datetime.date.today()).strftime("%d/%m/%Y")
            + " - "
            + (datetime.date.today() + datetime.timedelta(weeks=4)).strftime("%d/%m/%Y")
        )
        cab_slug = "cab_slug"
        form = RegResForm(
            data={
                "fechaDesdeHasta": fechaDesdeHasta,
                "cab_slug": cab_slug,
                "cantAdultos": 2,
                "cantMenores": 2,
            }
        )
        self.assertTrue(form.is_valid())

    def test_fecha_desde_fuera_de_rango_de_disponibilidad(self):
        """Testea que no sea exitosa la carga de una reserva en la que la fecha de ingreso
        no está dentro de ningún rango de disponibilidad de alquiler de la cabaña."""
        cab = get_a_cab()
        rango = Rango(
            fechaDesde=datetime.date.today(),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=6),
            cab=cab,
        )

        rango.save()
        fechaDesdeHasta = (
            (datetime.date.today() + datetime.timedelta(weeks=7)).strftime("%d/%m/%Y")
            + " - "
            + (datetime.date.today() + datetime.timedelta(weeks=8)).strftime("%d/%m/%Y")
        )
        cab_slug = "cab_slug"
        form = RegResForm(
            data={
                "fechaDesdeHasta": fechaDesdeHasta,
                "cab_slug": cab_slug,
                "cantAdultos": 2,
                "cantMenores": 2,
            }
        )
        self.assertFalse(form.is_valid())

    def test_fecha_desde_dentro_de_rango_de_una_reserva(self):
        """Testea que no sea exitosa la carga de una reserva que tiene la fecha de ingreso
        dentro de algún rango de reserva de la misma cabaña."""
        cab = get_a_cab()
        rango = Rango(
            fechaDesde=datetime.date.today(),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=6),
            cab=cab,
        )
        rango.save()

        crear_reserva(
            cab=cab,
            user=self.user,
            fechaDesde=datetime.date.today() + datetime.timedelta(weeks=2),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=4),
        )

        fechaDesdeHasta = (
            (datetime.date.today() + datetime.timedelta(weeks=3)).strftime("%d/%m/%Y")
            + " - "
            + (datetime.date.today() + datetime.timedelta(weeks=4)).strftime("%d/%m/%Y")
        )

        cab_slug = "cab_slug"
        form = RegResForm(
            data={
                "fechaDesdeHasta": fechaDesdeHasta,
                "cab_slug": cab_slug,
                "cantAdultos": 2,
                "cantMenores": 2,
            }
        )
        self.assertFalse(form.is_valid())

    # tests para la fechaHasta

    def test_fecha_hasta_antes_de_hoy(self):
        """Testea que no sea exitosa la carga de una reserva con la fecha hasta menor
        a la fecha actual."""
        cab = get_a_cab()
        rango = Rango(
            fechaDesde=datetime.date.today(),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=6),
            cab=cab,
        )
        cab.save()
        rango.save()
        fechaDesdeHasta = (
            (datetime.date.today()).strftime("%d/%m/%Y")
            + " - "
            + (datetime.date.today() - datetime.timedelta(weeks=1)).strftime("%d/%m/%Y")
        )
        cab_slug = "cab_slug"
        form = RegResForm(
            data={
                "fechaDesdeHasta": fechaDesdeHasta,
                "cab_slug": cab_slug,
                "cantAdultos": 2,
                "cantMenores": 2,
            }
        )
        self.assertFalse(form.is_valid())

    def test_fecha_hasta_igual_a_hoy(self):
        """Testea que la carga de una reserva con la fecha hasta igual al día de la fecha
        no sea exitosa, debido al hecho de que la cantidad mínima de noches es = 1 (2 días)"""
        cab = get_a_cab()
        rango = Rango(
            fechaDesde=datetime.date.today(),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=6),
            cab=cab,
        )
        cab.save()
        rango.save()
        fechaDesdeHasta = (
            (datetime.date.today()).strftime("%d/%m/%Y")
            + " - "
            + (datetime.date.today()).strftime("%d/%m/%Y")
        )
        cab_slug = "cab_slug"
        form = RegResForm(
            data={
                "fechaDesdeHasta": fechaDesdeHasta,
                "cab_slug": cab_slug,
                "cantAdultos": 2,
                "cantMenores": 2,
            }
        )
        self.assertFalse(form.is_valid())

    def test_fecha_hasta_fuera_de_rango_de_disponibilidad(self):
        """Testea que no sea exitosa la carga de una reserva con la fecha hasta fuera
        de rango de disponibilidad."""
        cab = get_a_cab()
        rango = Rango(
            fechaDesde=datetime.date.today(),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=6),
            cab=cab,
        )
        cab.save()
        rango.save()
        fechaDesdeHasta = (
            (datetime.date.today() + datetime.timedelta(weeks=1)).strftime("%d/%m/%Y")
            + " - "
            + (datetime.date.today() + datetime.timedelta(weeks=8)).strftime("%d/%m/%Y")
        )
        cab_slug = "cab_slug"
        form = RegResForm(
            data={
                "fechaDesdeHasta": fechaDesdeHasta,
                "cab_slug": cab_slug,
                "cantAdultos": 2,
                "cantMenores": 2,
            }
        )
        self.assertFalse(form.is_valid())

    def test_fecha_hasta_dentro_de_rango_de_una_reserva(self):
        """Testea que no sea exitosa la carga de una reserva con la fecha hasta dentro
        del rango de alguna reserva de la cabaña."""
        cab = get_a_cab()
        rango = Rango(
            fechaDesde=datetime.date.today(),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=6),
            cab=cab,
        )
        rango.save()

        crear_reserva(
            cab=cab,
            user=self.user,
            fechaDesde=datetime.date.today() + datetime.timedelta(weeks=2),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=4),
        )

        fechaDesdeHasta = (
            (datetime.date.today() + datetime.timedelta(weeks=1)).strftime("%d/%m/%Y")
            + " - "
            + (datetime.date.today() + datetime.timedelta(weeks=3)).strftime("%d/%m/%Y")
        )
        cab_slug = "cab_slug"
        form = RegResForm(
            data={
                "fechaDesdeHasta": fechaDesdeHasta,
                "cab_slug": cab_slug,
                "cantAdultos": 2,
                "cantMenores": 2,
            }
        )
        self.assertFalse(form.is_valid())

    # tests para las fechas dentro del rango ingresado

    def test_fecha_en_rango_ingresado_fuera_de_rango_de_disponibilidad(self):
        """Testea que no sea exitosa la carga de una reserva la cual tiene alguna fecha
        dentro de su rango fuera de algún rango de disponibilidad."""
        cab = get_a_cab()
        rango1 = Rango(
            fechaDesde=datetime.date.today(),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=4),
            cab=cab,
        )
        rango2 = Rango(
            fechaDesde=datetime.date.today() + datetime.timedelta(weeks=6),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=8),
            cab=cab,
        )
        cab.save()
        rango1.save()
        rango2.save()
        fechaDesdeHasta = (
            (datetime.date.today() + datetime.timedelta(weeks=1)).strftime("%d/%m/%Y")
            + " - "
            + (datetime.date.today() + datetime.timedelta(weeks=7)).strftime("%d/%m/%Y")
        )
        cab_slug = "cab_slug"
        form = RegResForm(
            data={
                "fechaDesdeHasta": fechaDesdeHasta,
                "cab_slug": cab_slug,
                "cantAdultos": 2,
                "cantMenores": 2,
            }
        )
        self.assertFalse(form.is_valid())

    def test_fecha_en_rango_ingresado_dentro_de_rango_de_una_reserva(self):
        """Testea que no sea exitosa la carga de una reserva la cual tiene alguna fecha
        en su rango dentro del rango de alguna reserva de la cabaña."""
        cab = get_a_cab()
        rango = Rango(
            fechaDesde=datetime.date.today(),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=5),
            cab=cab,
        )
        rango.save()

        crear_reserva(
            cab=cab,
            user=self.user,
            fechaDesde=datetime.date.today() + datetime.timedelta(weeks=2),
            fechaHasta=datetime.date.today() + datetime.timedelta(weeks=3),
        )

        fechaDesdeHasta = (
            (datetime.date.today() + datetime.timedelta(weeks=1)).strftime("%d/%m/%Y")
            + " - "
            + (datetime.date.today() + datetime.timedelta(weeks=4)).strftime("%d/%m/%Y")
        )

        cab_slug = "cab_slug"
        form = RegResForm(
            data={
                "fechaDesdeHasta": fechaDesdeHasta,
                "cab_slug": cab_slug,
                "cantAdultos": 2,
                "cantMenores": 2,
            }
        )
        self.assertFalse(form.is_valid())

    # los tests de cantidad de adultos y menores no los escribo todavía pq hay que definir
    # bien cómo es el límite, ahora la aplicación funciona con un máximo de 5 personas por
    # cabaña, entre adultos y menores, y con como mínimo, un adulto.


class RegistrarHuespedFormTest(TestCase):
    def test_datos_correctos(self):
        form = CrearHuespedForm(
            data={
                "nombre": "Samuel",
                "apellido": "Andres",
                "telefono": "3534237553",
            }
        )
        self.assertTrue(form.is_valid())

    def test_sin_ingresar_telefono(self):
        form = CrearHuespedForm(
            data={
                "nombre": "Samuel",
                "apellido": "Andres",
            }
        )
        self.assertFalse(form.is_valid())

    def test_sin_ingresar_apellido(self):
        form = CrearHuespedForm(
            data={
                "nombre": "Samuel",
                "telefono": "3534237553",
            }
        )
        self.assertFalse(form.is_valid())

    def test_sin_ingresar_nombre(self):
        form = CrearHuespedForm(
            data={
                "apellido": "Andres",
                "telefono": "3534237553",
            }
        )
        self.assertFalse(form.is_valid())
