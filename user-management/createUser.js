const AWS = require('aws-sdk');
const JWTVerifier = require('aws-jwt-verify');
require('dotenv').config();

const createUser = async (userName, password, email, phone, organization, group, locale, name, callback) => {
    AWS.config.update({
        region: 'us-east-2',
    });

    const cognitoIdentityServiceProvider = new AWS.CognitoIdentityServiceProvider();

    const params = {
        UserPoolId: process.env?.USER_POOL_ID,
        Username: userName,
        DesiredDeliveryMediums: ['EMAIL'],
        TemporaryPassword: password,
        UserAttributes: [
            {
                Name: 'email',
                Value: email,
            },
            {
                Name: 'email_verified',
                Value: 'false',
            },
            {
                Name: 'phone_number',
                Value: phone,
            },
            {
                Name: 'phone_number_verified',
                Value: 'false',
            },
            {
                Name: 'custom:organization',
                Value: organization,
            },
            {
                Name: 'custom:group',
                Value: group,
            },
            {
                Name: 'locale',
                Value: locale,
            },
            {
                Name: 'name',
                Value: name,
            }
        ],
    };

    try {
        await cognitoIdentityServiceProvider.adminCreateUser(params).promise();
        console.log('User created.')
        callback(null, "created.");
        return {};
    } catch (error) {
        callback("Failed. Check the logs.", 500);
        console.log(error);
        return error;
    }
};

const validateToken = async (token) => {
    const verifier = JWTVerifier.CognitoJwtVerifier.create({
        userPoolId: process.env?.USER_POOL_ID,
        tokenUse: "access",
        clientId: process.env?.CLIENT_ID,
      });
    return await verifier.verify(token);
}

exports.handler = async function (event, context, callback) {

    console.log("headers", event.headers);
    console.log("header type", typeof event.headers);
    const token = event.headers?.authorization?.split(" ")[1];

    const tokenData = await validateToken(token);
    console.log(tokenData);

    const queryStringParams = event.queryStringParameters;
    const userName = queryStringParams.username;
    const password = "TempPassword123!"
    const email = queryStringParams.email;
    const phone = queryStringParams.phone || "+15555555555";
    const organization = queryStringParams.organization;
    const group = queryStringParams.group;
    const locale = queryStringParams.locale || "en_US";
    const name = queryStringParams.name;

    await createUser(userName, password, email, phone, organization, group, locale, name, callback);
};
