package org.openstreetmap.josm.plugins.centerlines;

import java.awt.event.ActionEvent;

import org.openstreetmap.josm.actions.JosmAction;
import static org.openstreetmap.josm.tools.I18n.tr;
import org.openstreetmap.josm.plugins.centerlines.CenterlinesPlugin;

public class CenterlinesAction extends JosmAction {
    private static CenterlinesPlugin plugin;

    public CenterlinesAction(CenterlinesPlugin plugin) {
        super(tr("Generate centerline"), "centerlines",
              tr("Generates a centerline for any closed polygon."),
              null, false);

        this.plugin = plugin;
        this.setEnabled(true);
    }

    @Override
    public void actionPerformed(ActionEvent e) {
        if (!this.isEnabled()) {
            return;
        }

        this.plugin.execute();
    }
}
