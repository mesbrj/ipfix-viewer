import time
import pyfixbuf
from PySide6.QtCore import QModelIndex, Qt, QAbstractItemModel

from treeitem import TreeItem
from ipfix_treemodel_helper import file_collector, info_element_decoder, sub_tmplt_list_decoder


class TreeModel(QAbstractItemModel):

    def __init__(self, headers: list, ipfix_file_path: str, parent=None):
        super().__init__(parent)

        self.root_data = headers
        self.root_item = TreeItem(self.root_data.copy())
        self.setup_model_data(ipfix_file_path, self.root_item)

    def columnCount(self, parent: QModelIndex = None) -> int:
        return self.root_item.column_count()

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None

        if role != Qt.ItemDataRole.DisplayRole and role != Qt.ItemDataRole.EditRole:
            return None

        item: TreeItem = self.get_item(index)

        return item.data(index.column())

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEditable | QAbstractItemModel.flags(self, index)

    def get_item(self, index: QModelIndex = QModelIndex()) -> TreeItem:
        if index.isValid():
            item: TreeItem = index.internalPointer()
            if item:
                return item

        return self.root_item

    def headerData(self, section: int, orientation: Qt.Orientation,
                    role: int = Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.root_item.data(section)

        return None

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return QModelIndex()

        child_item: TreeItem = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def insertColumns(self, position: int, columns: int,
                      parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertColumns(parent, position, position + columns - 1)
        success: bool = self.root_item.insert_columns(position, columns)
        self.endInsertColumns()

        return success

    def insertRows(self, position: int, rows: int,
                   parent: QModelIndex = QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return False

        self.beginInsertRows(parent, position, position + rows - 1)
        column_count = self.root_item.column_count()
        success: bool = parent_item.insert_children(position, rows, column_count)
        self.endInsertRows()

        return success

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_item: TreeItem = self.get_item(index)
        if child_item:
            parent_item: TreeItem = child_item.parent()
        else:
            parent_item = None

        if parent_item == self.root_item or not parent_item:
            return QModelIndex()

        return self.createIndex(parent_item.child_number(), 0, parent_item)

    def removeColumns(self, position: int, columns: int,
                      parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveColumns(parent, position, position + columns - 1)
        success: bool = self.root_item.remove_columns(position, columns)
        self.endRemoveColumns()

        if self.root_item.column_count() == 0:
            self.removeRows(0, self.rowCount())

        return success

    def removeRows(self, position: int, rows: int,
                   parent: QModelIndex = QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return False

        self.beginRemoveRows(parent, position, position + rows - 1)
        success: bool = parent_item.remove_children(position, rows)
        self.endRemoveRows()

        return success

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return 0
        return parent_item.child_count()

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        if role != Qt.ItemDataRole.EditRole:
            return False

        item: TreeItem = self.get_item(index)
        result: bool = item.set_data(index.column(), value)

        if result:
            self.dataChanged.emit(index, index,
                                  [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])

        return result

    def setHeaderData(self, section: int, orientation: Qt.Orientation, value,
                      role: int = None) -> bool:
        if role != Qt.ItemDataRole.EditRole or orientation != Qt.Orientation.Horizontal:
            return False

        result: bool = self.root_item.set_data(section, value)

        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result

    def setup_model_data(self, ipfix_file_path: str, root_tree: TreeItem):

        col_count = self.root_item.column_count()
        root_tree.insert_children(root_tree.child_count(), 1, col_count)

        tree_headers = root_tree.last_child()
        data = [f" IPFIX File: {ipfix_file_path} ", None, None] 
        for column in range(len(data)):
            tree_headers.set_data(column, data[column])

        try:
            id = 0
            for rec in file_collector(ipfix_file_path):
                if not "flowStartMilliseconds" in rec:
                    continue
                id += 1
                flow_start = flow_end = duration = bidirectional = None

                for field in rec.iterfields():

                    if field.name == "flowStartMilliseconds":
                        s, ms = divmod(field.value, 1000)
                        flow_start = '{}.{:03d}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(s)), ms)
                        flow_start_epoch = field.value

                    elif field.name == "flowEndMilliseconds" and flow_start:
                        s, ms = divmod(field.value, 1000)
                        flow_end = '{}.{:03d}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(s)), ms)
                        flow_end_epoch = field.value
                        duration = (int(flow_end_epoch) - int(flow_start_epoch))
                        if duration/1000 >= 60:
                            duration = f"{(duration/1000)/60:5.3f} minutes"
                        else:
                            duration = f"{duration/1000} seconds"

                        tree_headers.insert_children(
                            tree_headers.child_count(), 1, col_count
                        )
                        flow_level = tree_headers.last_child()
                        data = [
                            f"[{id}] Bi-directional Flow Duration: {duration}",
                            f"Start: {flow_start}  |  End: {flow_end}",
                            f"{pyfixbuf.DataType.get_name(field.ie.type)}"
                        ]
                        for column in range(len(data)):
                            flow_level.set_data(column, data[column])

                    elif field.ie.type == pyfixbuf.DataType.SUB_TMPL_LIST and flow_start and flow_end:
                        sub_tmplt_list_decoder(rec, field, flow_level, col_count)

                    elif field.ie.type == pyfixbuf.DataType.SUB_TMPL_MULTI_LIST and flow_start and flow_end:
                        continue

                    elif flow_start and flow_end:
                        if info_element_decoder(field, flow_level, col_count) and "reverse" in field.name:
                            bidirectional = True

                if not bidirectional and flow_start and flow_end:
                    data = [
                        f"[{id}] One-way Flow Duration: {duration}",
                        f"Start: {flow_start}  |  End: {flow_end}",
                        None
                    ]
                    for column in range(len(data)):
                        flow_level.set_data(column, data[column])

        except Exception as e:
            error_data = [f"Error: {str(e)}", "Failed to process IPFIX file", None]
            tree_headers.insert_children(tree_headers.child_count(), 1, col_count)
            error_level = tree_headers.last_child()
            for column in range(len(error_data)):
                error_level.set_data(column, error_data[column])

    def _repr_recursion(self, item: TreeItem, indent: int = 0) -> str:
        result = " " * indent + repr(item) + "\n"
        for child in item.child_items:
            result += self._repr_recursion(child, indent + 2)
        return result

    def __repr__(self) -> str:
        return self._repr_recursion(self.root_item)
