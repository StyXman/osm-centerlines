// fuck you, Java. really, go fuck yourself.
// you force me to create a new file, duplicate import lines,
// just for 6 fucking lines of code. way to go, piece of shit.

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
