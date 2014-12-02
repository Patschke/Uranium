import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1
import QtQuick.Controls.Styles 1.1

Panel {
    title: "Files"

    contents: ColumnLayout {
        Layout.preferredWidth: 200
        Layout.preferredHeight: 400

        Button {
            Layout.fillWidth: true
            text: "Open File"
            onClicked: fileDialog.open()
        }

        TableView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            TableViewColumn { role: "text" }

            headerVisible: false

            model: ListModel {
                id: fileModel
            }
        }

        Button {
            Layout.fillWidth: true
            text: "Machine"
            onClicked: messageDialog.open()
            style: ButtonStyle 
            { 
                label: Rectangle
                {  
                    Layout.fillWidth: true
                    color: "transparent"
                    anchors.centerIn: parent
                    
                    Row {
                        anchors.centerIn: parent;
                        width: childrenRect.width;
                        height: childrenRect.height;
                        spacing:4
                        Image
                        {
                            id:machineButtonIcon
                            source: "../../../Resources/icon_ultimaker2.png" //TODO: HARDCODED
                        }
                        Text 
                        {
                            id:machineButtonText
                            text: "Machine"
                            font.pointSize: 20
                            color:"white"
                        }
                       
                    }
                }
                background: Rectangle 
                {
                    implicitWidth: 100
                    implicitHeight: 50
                    border.width: 1
                    border.color: "#404040"
                    gradient: Gradient 
                    {
                        GradientStop { position: 0; color: "#48BCDD"}
                        GradientStop { position: 1; color: "#6CCBE1"}
                    }
                }
            }
        }
    }

    FileDialog {
        id: fileDialog

        title: "Choose files"
        modality: Qt.NonModal
        selectMultiple: true

        onAccepted: {
            for(var i in fileDialog.fileUrls) {
                fileModel.append({ "text": fileDialog.fileUrls[i] })
            }
        }
    }
}
