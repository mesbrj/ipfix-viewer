import sys
import pyfixbuf
import pyfixbuf.cert

if not len(sys.argv) == 2:
    print(f"Usage: {sys.argv[0]} <ipfix_file>")
    sys.exit(1)
ipfix_file = sys.argv[1]

infomodel = pyfixbuf.InfoModel()
pyfixbuf.cert.add_elements_to_model(infomodel)

session = pyfixbuf.Session(infomodel)

collector = pyfixbuf.Collector()
collector.init_file(ipfix_file)

buffer = pyfixbuf.Buffer(auto=True)
buffer.init_collection(session,collector)

def stl_decoder(record, field_name):
    stl = record.get_stl_list_entry(field_name)
    if len(stl) != 0:
        print(f"\n[ SUB_TMPL_LIST: {field_name} ]\n")
        for sub in stl:
            for sub_field in sub.iterfields():
                if sub_field.ie.type == pyfixbuf.DataType.SUB_TMPL_LIST:
                    stl_decoder(sub, sub_field.name)
                else:
                    info_element_decoder(sub_field)

def info_element_decoder(field):
    field_value = None
    if isinstance(field.value, int) or isinstance(field.value, float):
        if field.value == 0:
            return
    if field.ie.type == pyfixbuf.DataType.STRING and field.value == "":
        return
    if field.ie.type == pyfixbuf.DataType.BASIC_LIST:
        if field.value == [] or field.value == "":
            return
        field_value = f"{field[4]}"[1:-1].replace("'", "")
    if not field_value:
        field_value = field.value
    print(f"#  {pyfixbuf.DataType.get_name(field.ie.type)}|{field.name} --> {field_value}")

record_count = 0
for data in buffer:
    if not "flowStartMilliseconds" in data:
        continue
    record_count += 1
    print(f"\n[ Record {record_count} ]\n")
    for field in data.iterfields():
        if (
            field.ie.type != pyfixbuf.DataType.SUB_TMPL_MULTI_LIST
            and field.ie.type != pyfixbuf.DataType.SUB_TMPL_LIST
        ):
            info_element_decoder(field)
        elif field.ie.type == pyfixbuf.DataType.SUB_TMPL_LIST:
            stl_decoder(data, field.name)
        else:
            print(f"|!!!|{pyfixbuf.DataType.get_name(field.ie.type)}|{field.name} --> {field.value}")
    print("\n"+"="*65+"\n")


