import pyfixbuf
import pyfixbuf.cert
import ipaddress

from treeitem import TreeItem

def file_collector(file_path: str) -> pyfixbuf.Buffer:

    infomodel = pyfixbuf.InfoModel()
    pyfixbuf.cert.add_elements_to_model(infomodel)

    session = pyfixbuf.Session(infomodel)

    collector = pyfixbuf.Collector()
    collector.init_file(file_path)

    buffer = pyfixbuf.Buffer(auto=True)
    buffer.init_collection(session,collector)

    return buffer

def info_element_decoder(field, parent: TreeItem, col_count: int):
    field_value = None
    if (isinstance(field.value, int) or isinstance(field.value, float)) and field.value == 0:
        return
    if field.ie.type == pyfixbuf.DataType.STRING and field.value == "":
        return
    elif field.ie.type == pyfixbuf.DataType.BASIC_LIST:
        if field.value == [] or field.value == "":
            return
        if len(field) > 4:
            field_value = f"{field[4]}"[1:-1].replace("'", "")
        else:
            field_value = str(field.value)
    if not field_value:
        field_value = field.value
    if field.ie.type == pyfixbuf.DataType.IP4ADDR:
        field_value = str(ipaddress.IPv4Address(field_value))
    elif field.ie.type == pyfixbuf.DataType.IP6ADDR:
        field_value = str(ipaddress.IPv6Address(field_value))
    elif isinstance(field_value, (bytearray, bytes)):
        try:
            decoded_text = field_value.decode('utf-8', errors='ignore')
            if decoded_text.isprintable():
                field_value = f"'{decoded_text}' ({len(field_value)} bytes)"
            else:
                field_value = ' '.join(f'{b:02x}' for b in field_value)
        except:
            field_value = str(field_value)

    info_element = [field.name, field_value, pyfixbuf.DataType.get_name(field.ie.type)]
    parent.insert_children(
        parent.child_count(), 1, col_count
    )
    info_element_level = parent.last_child()
    for column in range(len(info_element)):
        info_element_level.set_data(column, info_element[column])
    return True

def sub_tmplt_list_decoder(record, field, parent: TreeItem, col_count: int):
    parent.insert_children(
        parent.child_count(), 1, col_count
    )
    stl_node = parent.last_child()
    if field.name == "yafDPIList":
        data = ["YAF Deep Packet Inspection Info-Elements", None, None]
    else:
        data = [field.name, None, None]
    for column in range(len(data)):
        stl_node.set_data(column, data[column])
    stl = record.get_stl_list_entry(field.name)
    if len(stl) != 0:
        for sub in stl:
            for sub_field in sub.iterfields():
                if sub_field.ie.type == pyfixbuf.DataType.SUB_TMPL_LIST:
                    sub_tmplt_list_decoder(sub, sub_field, stl_node, col_count)
                else:
                    info_element_decoder(sub_field, stl_node, col_count)



