from apps.payments.models import ServiceProviderWallet, WalletLog


class WalletManagementMixin(object):
    def __init__(self, wallet_owner, action_user, action_type, amount_transacted):
        self.wallet_owner = wallet_owner
        self.action_user = action_user
        self.action_type = action_type
        self.amount_transacted = amount_transacted

    def run(self):
        self.__process_wallet_transaction()

    def __process_wallet_transaction(self):
        try:
            if self.action_type in ["Withdraw", "Subscription Payment"]:
                self.__process_withdrawal()

            elif self.action_type in ["Refund", "AirBnB Booking", "Ticket Booking", "Room Booking"]:
                self.__process_deposit()
        except Exception as e:
            raise e

    def __process_withdrawal(self):
        try:
            wallet = ServiceProviderWallet.objects.get(user=self.wallet_owner)
            wallet.balance -= self.amount_transacted
            wallet.save()

            self.write_wallet_log(wallet, self.action_user,
                                self.amount_transacted, self.action_type)
        except Exception as e:
            raise e

    def __process_deposit(self):
        try:
            wallet = ServiceProviderWallet.objects.get(user=self.wallet_owner)

            wallet.balance += self.amount_transacted
            wallet.save()

            self.write_wallet_log(wallet, self.action_user,
                                self.amount_transacted, self.action_type)

        except Exception as e:
            raise e

    def write_wallet_log(self, wallet, actioned_by, amount, transaction_type):
        try:
            WalletLog.objects.create(
                wallet=wallet,
                actioned_by=actioned_by,
                amount=amount,
                transaction_type=transaction_type
            )
        except Exception as e:
            raise e
