from django.db import models
from paybills.models import BasicItem

# Create your models here.

class Period(BasicItem):
    """
    This is the product thats being purchased.
    """

    # The price should be calculated taking into account
    # User.expiration and current User.max_users attrs.
    price = models.IntegerField(null=False, default=0)

    # This is the max number of users that our customer
    # will purchase for a period of time. There is a difference
    # between current number of users and max_users. If the customer
    # attempt to add more users to his account than the max then he is
    # asked to upgrade his limits. This way i think we may be able
    # to implement subscription.
    max_users = models.IntegerField(null=False, default=3,
    help_text="Max users until the expiration.")

    expiration = models.DateField(null=True, 
    blank=False, help_text="Example: year-month-day")

    total = models.FloatField(null=False, default=0)
    paid  = models.BooleanField(default=False)

    def __str__(self):
        return ('Paid: {paid}' 
        'Price: {price}' 
        'Expiration: {expiration}' 
        'Max Users: {max_users}').format(paid=self.paid, 
            price=self.price, expiration=self.expiration, 
                max_users=self.max_users)

