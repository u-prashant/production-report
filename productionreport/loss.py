class LossQuantity:
    @staticmethod
    def get(oci, loss_df, dept):
        quantity = loss_df[(loss_df['OCI'] == oci) & loss_df['Department'] == dept]['Quantity']
        if quantity is None:
            quantity = 0
        return quantity
