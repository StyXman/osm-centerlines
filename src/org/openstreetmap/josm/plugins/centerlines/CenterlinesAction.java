package org.openstreetmap.josm.plugins.centerlines;

import java.awt.event.ActionEvent;

import org.openstreetmap.josm.actions.JosmAction;
import static org.openstreetmap.josm.tools.I18n.tr;

public class CenterlinesAction extends JosmAction {
    public CenterlinesAction() {
        super(tr("Generate centerline"), "centerlines",
              tr("Generates a centerline for any closed polygon."),
              null, false);
        this.setEnabled(false);
    }

    @Override
    public void actionPerformed(ActionEvent e) {
    }
}
