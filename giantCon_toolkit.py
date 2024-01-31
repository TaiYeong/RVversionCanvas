from rv import commands, runtime
import os


def init_con_mu_command():
    muCode = """
    {
        require export_utils;

        print("I'm at the beginning.\n");
        bind("custom-export-movie-request", \: (void;Event event) {
            let contents = event.contents(),
                    parts = contents.split(";"),
                    start = int(parts[0]),
                    end = int(parts[1]),
                    name = parts[2];

            print("I've figured out my contents.");

            bool blocking=false;
            string conversion="default";
            string codec = "libx264";
            let temp = export_utils.makeTempSession(conversion);

            string[] args =
            {
                temp,
                "-o", name,
                "-t",  "%d-%d" % (start, end),
                "-iomethod", 0
            };

            print("About to run RVIO!\n");

            if (blocking)
            {
                export_utils.rvio_blocking("Export Movie", args, export_utils.removeSession(temp));
                return;
            }
            else
            {
                
                State state = data();
                state.externalProcess = export_utils.rvio("Export Movie", args, export_utils.removeSession(temp));
                toggleProcessInfo();
                redraw();
                return;
            }
        },
        "Initiate custom movie export");

        print("Bound custom export.\n");

        1;
    }
    """
    runtime.eval(muCode, ['rvui', 'app_utils', 'python', 'commands', 'rvtypes'])




def do_giant_convert():
    savePath = commands.saveFileDialog (True, None, os.path.expanduser("~"), False)
    if savePath:
        start = commands.inPoint()
        end = commands.outPoint()
        commands.sendInternalEvent("custom-export-movie-request", "%d;%d;%s" % (start, end, savePath) )


