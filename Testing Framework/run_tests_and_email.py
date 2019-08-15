import smtplib
from time import ctime
from email.message import EmailMessage
import example_contour_module as contour
import example_geom_module as geom
# import example_mesh_module as mesh
import example_path_module as path
import example_solid_model_module as solid_model

#
# Reference for sending email in Python:
# https://www.youtube.com/watch?v=JRCJ6RtE3xU
#

recipients = [
    "neilbalch@gmail.com",
    # "gdmaher@stanford.edu"
]

# https://stackoverflow.com/a/57449397/3339274
def flatten_multidimensional_list(nested_list):
    """ Return a list after transforming the inner lists
        so that it's a 1-D list.

    >>> flatten([[[],["a"],"a"],[["ab"],[],"abc"]])
    ['a', 'a', 'ab', 'abc']
    """
    if not isinstance(nested_list, list):
        return(nested_list)

    res = []
    for l in nested_list:
        if not isinstance(l, list):
            res += [l]
        else:
            res += flatten_multidimensional_list(l)

    return(res)

# Get 2D list of raw output strings ([test module][lines]).
raw_output = []
raw_output.append(contour.contour_tests(colors=False))
raw_output.append(geom.geom_tests(colors=False))
# output.append(mesh.mesh_tests(colors=False))
raw_output.append(path.path_tests(colors=False))
raw_output.append(solid_model.solid_model_tests(colors=False))

# Flatten the 2D list ([lines]).
flattened_output = flatten_multidimensional_list(raw_output)

# Create string for the plain text message.
plain_text_msg = ""
for line in flattened_output:
  plain_text_msg += line
  plain_text_msg += "\n"

tests_contain_fail = False

# Make deep copy of flattened output and format it for email HTML.
formatted_output = flattened_output[:]
for i in range(len(formatted_output)):
    # If a test failed, record that for display in the subject line.
    if "[ FAIL ]" in formatted_output[i]:
        tests_contain_fail = True

    # Color code the PASS and FAIL thingies
    formatted_output[i] = formatted_output[i].replace("[ PASS ]",
                          "[ <span style=\"color:Green\">PASS</span> ]")
    formatted_output[i] = formatted_output[i].replace("[ FAIL ]",
                          "[ <span style=\"color:Red\">FAIL</span> ]")
    # Apply header tags to the test module summary lines.
    if "Results for" in formatted_output[i]:
        formatted_output[i] = "<h3>" + formatted_output[i] + "</h3>"
    if "tests completed:" in formatted_output[i]:
        formatted_output[i] = "<h4>" + formatted_output[i] + "</h4>"
    # Replace string \n and \t chars with HTML equivalents.
    formatted_output[i] = formatted_output[i].replace("\n", "<br>")
    formatted_output[i] = formatted_output[i].replace("\t", "&#9;")
    # Add line break to the end of every line.
    formatted_output[i] += "<br>"

# print(formatted_output)

# Format of ./credentials.file, verbatim:
# [GMAIL ACCOUNT EMAIL ADDRESS]
# [GMAIL ACCOUNT PASSWORD]
with open("credentials.file", "r") as file:
    credentials = file.read().split("\n")
    GMAIL_ADDRESS = credentials[0]
    GMAIL_PASSWD = credentials[1]

# Datetime: https://stackoverflow.com/a/48283832/3339274
msg = EmailMessage()
msg["Subject"] = ("[CI " + ("FAIL" if tests_contain_fail else "PASS")
                 + "] SimVascular Python API Unit Test Report (" + ctime() + ")")
msg["From"] = GMAIL_ADDRESS
msg["To"] = recipients

# Add plain-text version.
msg.set_content(plain_text_msg)

# Add HTML version of message.
msg.add_alternative("""\
<!DOCTYPE html>
<html>
    <body>
""" + "\n".join(formatted_output)
+ """
    </body>
</html>
""", subtype="html")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(GMAIL_ADDRESS, GMAIL_PASSWD)
    smtp.send_message(msg)