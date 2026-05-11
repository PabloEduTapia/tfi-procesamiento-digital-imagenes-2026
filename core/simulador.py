from core.protanopia import aplicar_protanopia

# Futuro:
# from core.deuteranopia import aplicar_deuteranopia
# from core.tritanopia import aplicar_tritanopia


def simular_daltonismo(imagen, tipo):

    if tipo == "protanopia":
        return aplicar_protanopia(imagen)

    # Futuro:
    # elif tipo == "deuteranopia":
    #     return aplicar_deuteranopia(imagen)

    # elif tipo == "tritanopia":
    #     return aplicar_tritanopia(imagen)

    else:
        print("Tipo de daltonismo no válido")
        return imagen