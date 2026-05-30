import factory
from faker import Faker
from src.models import QRCodeModel

fake = Faker()


class QRCodeFactory(factory.Factory):
    """
    Factory Boy class to generate realistic mock QRCodeModel objects for unit and integration tests.
    """

    class Meta:
        model = QRCodeModel

    title = factory.LazyAttribute(lambda _: f"QR - {fake.company()}")
    target_url = factory.LazyAttribute(lambda _: fake.url())
    s3_key = factory.LazyAttribute(lambda _: f"qrcodes/{fake.uuid4()}.png")
    s3_url = factory.LazyAttribute(
        lambda o: f"http://localhost:4566/qrcode-bucket/{o.s3_key}"
    )
    scan_count = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=100))
