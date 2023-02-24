mail_html_content = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en" style="height: 100%;">

<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />

    <title>Invitation Emailer</title>
</head>

<body style="margin: 0; padding: 0; height: 100%;">
    <table border="0" bgcolor="#f6f6f6" cellpadding="0" cellspacing="0" width="100%" height="100%" style="
        height: 100%;
        background-color: #f6f6f6;
        font-family: Arial, Helvetica, sans-serif;
        margin-top: 0;
        margin-right: 0;
        margin-bottom: 0;
        margin-left: 0;
        border: 0;
        ">
        <tr>
            <td align="center" valign="top">
                <table border="0" cellpadding="0" cellspacing="0" width="580" style="
                    padding-right: 16px;
                    padding-left: 16px;
                    margin-top: 32px;
                    margin-right: auto;
                    margin-bottom: 32px;
                    margin-left: auto;
                    ">
                    <tr>
                        <td align="center" valign="top" style="text-align: center;">
                            <img src="cid:image1" alt="Facet logo" height="46px" />
                        </td>
                    </tr>
                    <tr>
                        <td align="center" valign="top">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="
                                width: 100%;
                                padding-top: 32px;
                                padding-right: 0;
                                padding-left: 0;
                                margin-top: 0;
                                margin-right: 0;
                                margin-bottom: 0;
                                margin-left: 0;
                            ">
                                <tr>
                                    <td align="center" valign="top">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="
                                                width: 100%;
                                                margin-top: 0;
                                                margin-right: 0;
                                                margin-bottom: 0;
                                                margin-left: 0;
                                                ">
                                            <tr>
                                                <td align="left" valign="top">
                                                    <table border="0" bgcolor="#ffffff" cellpadding="0" cellspacing="0"
                                                        width="100%" style="
                                                            width: 100%;
                                                            background-color: #ffffff;
                                                            border-width: 1px;
                                                            border-style: solid;
                                                            border-color: #dfdfdf;
                                                            padding-top: 24px;
                                                            padding-right: 24px;
                                                            padding-bottom: 24px;
                                                            padding-left: 24px;
                                                            margin-top: 0;
                                                            margin-right: 0;
                                                            margin-bottom: 0;
                                                            margin-left: 0;
                                                            border-radius: 6px;
                                                        ">
                                                        <tr>
                                                            <td align="left" valign="top" style="padding-top: 24px">
                                                                <p style="
                                                                    font-size: 16px;
                                                                    line-height: 22px;
                                                                    font-weight: normal;
                                                                    color: #565452;
                                                                    margin-top: 0;
                                                                    margin-right: 0;
                                                                    margin-bottom: 0;
                                                                    margin-left: 0;
                                                                    ">
                                                                    {{invite_sender_name}} with
                                                                    {{invite_sender_organization}} has invited you to
                                                                    use FACET to collaborate with them. Use
                                                                    the button below to set up your account and get
                                                                    started.
                                                                </p>
                                                                <div
                                                                    style="text-align: center; padding-top: 32px; padding-bottom: 32px;">
                                                                    <a href="{{signup_url}}"
                                                                        style="display: inline-block; background-color: #002D62; font-size: 14px; line-height: 21px; font-weight: 700; color: #ffffff; padding-top: 8px; padding-right: 16px; padding-bottom: 8px; padding-left: 16px; text-decoration: none; border-radius: 4px;">View
                                                                        Invitation</a>
                                                                </div>
                                                                <p style="
                                                                font-size: 16px;
                                                                line-height: 22px;
                                                                font-weight: normal;
                                                                color: #565452;
                                                                margin-top: 0;
                                                                margin-right: 0;
                                                                margin-bottom: 24px;
                                                                margin-left: 0;
                                                                ">If you have any questions for {{invite_sender_name}},
                                                                    you can reply to
                                                                    this email and it will go right to them.
                                                                    Alternatively, feel free to contact
                                                                    our customer success team anytime. (We're lightning
                                                                    quick at
                                                                    replying.) We also offer live chat during business
                                                                    hours.</p>
                                                                <div style="margin-bottom: 24px;">
                                                                    <p style="
                                                                font-size: 16px;
                                                                line-height: 22px;
                                                                font-weight: normal;
                                                                color: #565452;
                                                                margin-top: 0;
                                                                margin-right: 0;
                                                                margin-bottom: 0;
                                                                margin-left: 0;
                                                                ">Welcome aboard,</p>
                                                                    <p style="
                                                                font-size: 16px;
                                                                line-height: 22px;
                                                                font-weight: normal;
                                                                color: #565452;
                                                                margin-top: 0;
                                                                margin-right: 0;
                                                                margin-bottom: 0;
                                                                margin-left: 0;
                                                                ">The FACET Team</p>
                                                                </div>
                                                                <p style="
                                                                font-size: 14px;
                                                                line-height: 20px;
                                                                font-weight: normal;
                                                                color: #565452;
                                                                margin-top: 0;
                                                                margin-right: 0;
                                                                margin-bottom: 0;
                                                                margin-left: 0;
                                                                ">PS. Need help getting started? Check out our <a
                                                                        href="/" target="_blank"
                                                                        style=" color: #007FFF;">help documentation</a>.
                                                                </p>
                                                                <div
                                                                    style="margin-top: 16px; margin-bottom: 16px; border-bottom-width: 1px; border-bottom-style: solid; border-bottom-color: #e8e8e8;">
                                                                </div>
                                                                <p style="
                                                                font-size: 12px;
                                                                line-height: 16px;
                                                                font-weight: normal;
                                                                color: #565452;
                                                                margin-top: 0;
                                                                margin-right: 0;
                                                                margin-bottom: 0;
                                                                margin-left: 0;
                                                                ">
                                                                    If you're having trouble with the button above, copy
                                                                    and paste the URL below into your web
                                                                    browser.
                                                                </p>
                                                                <p style="
                                                                font-size: 12px;
                                                                line-height: 16px;
                                                                font-weight: normal;
                                                                color: #565452;
                                                                margin-top: 0;
                                                                margin-right: 0;
                                                                margin-bottom: 0;
                                                                margin-left: 0;
                                                                "><a href={{action_url}} target="_blank"
                                                                        style=" color: #007FFF;">{{action_url}}</a></p>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" valign="top">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="
                                                width: 100%;
                                                margin-top: 0;
                                                margin-right: 0;
                                                margin-bottom: 0;
                                                margin-left: 0;
                                            ">
                                            <tr>
                                                <td align="center" valign="top"
                                                    style="padding-top: 32px; text-align: center;">
                                                    <p style="
                                                            font-size: 12px;
                                                            line-height: 16px;
                                                            color: #a6a5a4;
                                                            margin-top: 0;
                                                            margin-right: 0;
                                                            margin-bottom: 0;
                                                            margin-left: 0;
                                                        ">
                                                        FACET
                                                    </p>
                                                    <p style="
                                                            font-size: 12px;
                                                            line-height: 16px;
                                                            color: #a6a5a4;
                                                            margin-top: 0;
                                                            margin-right: 0;
                                                            margin-bottom: 0;
                                                            margin-left: 0;
                                                        ">
                                                        Address Line 1
                                                    </p>
                                                    <p style="
                                                            font-size: 12px;
                                                            line-height: 16px;
                                                            color: #a6a5a4;
                                                            margin-top: 0;
                                                            margin-right: 0;
                                                            margin-bottom: 0;
                                                            margin-left: 0;
                                                        ">
                                                        Address Line 2
                                                    </p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>

</html>
"""