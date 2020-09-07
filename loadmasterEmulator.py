import argparse
import json

import requests
import requests.cookies
import time
import hashlib
import subprocess



def generate_magic(seed, verify):
    salt = 'PJAC' if verify else 'RM-PJAC'
    hash = hashlib.md5()
    hash.update("{}{}".format(seed, salt).encode('utf-8'))
    magic = hash.hexdigest()
    return magic


def first_call(options, seed, magic):
    response = requests.post(options.host + '/licserv.php/initial/' + magic, headers={"User-Agent": "LicUpdate: {}".format(seed)})
    #a = response.url
    #print(a, magic_from_alsi)
    return response


def second_call(command, options, cookies, data, magic):
    try:
        responseCookie = requests.post("{}/licserv.php/{}/{}".format(options.host, command, magic), cookies=cookies, data=data)
        list_of_licenses = responseCookie.text
        #print(list_of_licenses)
        return list_of_licenses

    except Exception as e:
       print("EXCEPTION THROWN")
       print(e)
       exit(1)
#




# TODO: TASK1 Accept Command Line arguements using argparse library
# python3 loadmaster_license_emulator.py -k jlim@kemptechnologies.com -p kemptech.jlim
def main():
    parser = argparse.ArgumentParser(
        description='Licensing emulator for Kemp 360 Central',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-H', '--host', dest='host',
                        default='https://alsi-stage.kemptechnologies.com',
                        help='ALSI server to license against')

    parser.add_argument('-k', '--kemp-id', dest='kemp_id',
                        default='afabiano@kemptechnologies.com', help='Kemp ID')
    parser.add_argument('-p', '--password', dest='password',
                        default='kemptech.afabiano', help='ALSI Password')
    parser.add_argument('-S', '--spla', action='store_true',
                        help='Enable SPLA flag')
    parser.add_argument('-b', '--bsku', dest='bsku',
                        help='Base SKU')

    parser.add_argument('-a', '--acc', dest='acc', default='mmw14-kuw9w-spwzg-pvwzg',
                        help='Access Code')

    parser.add_argument('-u', '--uuid', dest='uuid',
                        help='UUID')

    parser.add_argument('-f', '--free', dest='free',
                        help='Free VLM flag (0/1)')

    parser.add_argument('-s', '--sn', dest='sn',
                        help='Serial Number')

    parser.add_argument('-v', '--version', dest='version',
                        help='Version Number')

    parser.add_argument('-o  ', '--order-id', dest='order_id',
                        help='Order ID')

    parser.add_argument('-V', '--virtual', dest='virtual',
                        help='Virtual Flag')

    parser.add_argument('-af', '--azure_flag', dest='azure_flag',
                        help='Azure Flag')

    parser.add_argument('-ac', '--azure_containerid', dest='azure_containerid',
                        help='Azure Container ID')

    parser.add_argument('-ari', '--azure_roleinstanceid', dest='azure_roleinstanceid',
                        help='Azure Role Instance ID')

    parser.add_argument('-awsf', '--aws_flag', dest='aws_flag',
                        help='AWS Flag')

    parser.add_argument('-ai', '--aws_instanceid', dest='aws_instanceid',
                        help='AWS Instance ID')

    parser.add_argument('-ait', '--aws_instancetype', dest='aws_instancetype',
                        help='AWS Instance Type')

    parser.add_argument('-aai', '--aws_accountid', dest='aws_accountid',
                        help='AWS Account ID')

    parser.add_argument('-ar', '--aws_region', dest='aws_region',
                        help='AWS Region')


    parser.add_argument('-aii', '--aws_imageid', dest='aws_imageid',
                        help='AWS Image ID')

    #todo: Additionally hard code
    parser.add_argument('-mt', '--mtype', dest='mtype',
                        help='mtype')#

    parser.add_argument('-z', '--zclm', dest='zclm',
                        help='zclm') #

    options = parser.parse_args()

    seed = str(time.time())
    magic = generate_magic(seed, verify=False)#'RM-PJAC')
    response = first_call(options, seed, magic)
    magic_from_alsi = response.text.split(" ")[1].strip()

    verification_magic = generate_magic(seed, verify=True)#'PJAC')

    if magic_from_alsi != verification_magic:
        print("verification of magic string failed")
        return False

    data = {
        "name": options.kemp_id,
        "password": options.password,
        "order": options.order_id,
        "access": options.acc,
        "vlm": options.virtual,
        "id": options.sn,
        "lmvers": options.version,
        "uuid": options.uuid,
        "mtype": options.mtype,
        "sku": options.bsku,
        "zclm": options.zclm
    }

    list_of_licenses = second_call("getlicensetypes", options, response.cookies, data, magic)

    if 'available' == 0:
        print("verification Response is failed")
        return False
    print("response cookie verification succeeded\n\n")

    # TODO: Task 3 Display List of licenses for firmware versions greater or equal to 7.2.36

    print("--- List of available License Type---")
    licenses = json.loads(list_of_licenses)
    count = 1
    while count <= len(licenses):
        for licenseType in licenses['categories']:
            print("\n[" + licenseType['description'] + "]:")
            for k in licenseType['licenseTypes']:
                name = k['name']
                available = k['available']
                print("[" + str(count) + "] = " + str(name) + " | " + "Available: " + str(available))
                count += 1

    count = 1
    num = input("\nEnter license number: ")
    option = int(num)
    while count <= len(licenses):
        for licenseType in licenses['categories']:
            for k in licenseType['licenseTypes']:
                name = k['name']
                available = k['available']
                if (option == count):
                    ID = k['id']
                    print("\n[" + str(count) + "] = " + str(name) + " | " + "Available: " + str(available) + "\n")
                count += 1

    data['lic_type_id'] = ID
    seed = str(time.time())
    magic = generate_magic(seed, verify=False)  # 'RM-PJAC')
    response = first_call(options, seed, magic)
    magic_from_alsi = response.text.split(" ")[1].strip()
    verification_magic = generate_magic(seed, verify=True)  # 'PJAC')

    if magic_from_alsi != verification_magic:
        print("verification of magic string failed")
        return False

    target_licenses = second_call("getlicense", options, response.cookies, data, magic)
    if 'available' == 0:
        print("verification Response is failed")
        return False
    print("response cookie verification succeeded\n\n")
    print(target_licenses+"\n\n")


    #TODO: Task 4 Decrypt the BLOB and display the result.
    # write target licens# with open blahabh
    print("Decrypt response from ALSI:\n")

    with open( 'genchk.txt','w') as file_object:
        file_object.write(target_licenses)

    decrypter = subprocess.Popen(["../bin/genchk", "-D", "-b", "genchk.txt"])
    #decrypter = subprocess.Popen(["./../bin/genchk -D -b".format("genchk.txt")])
    out = decrypter.communicate()[0]
    print(out)
    # print the output after decrypt








####################################################################################################################################################################
    # TODO: TASK2 Implement security handshake between emulator and ALSI BLOB(Binary large Objects)
    # TODO: For ALSI to send a BLOB back to ALSI. WE have to do a security check between ALSI and the emulator to simulate a real Loadmaster

    # TODO: First Call
    # Create the seed
#seed = str(time.time()) # Get current time in seconds epoch on Linux

#
# def first_call(options, seed):
#     #seed = str(time.time())  # Get current time in seconds epoch on Linux
#     # Magic string with MD5
#     hash = hashlib.md5()
#     hash.update("{}RM-PJAC".format(seed).encode('utf-8'))
#     magic = hash.hexdigest()
#     magic = generate_magic(seed, 'RM-PJAC')
#
#     response = requests.post(options.host + '/licserv.php/initial/' + magic, headers={"User-Agent": "LicUpdate: {}".format(seed)})
#     a = response.url
#     magic_from_alsi = response.text.split(" ")[1].strip()
#     print(a, magic_from_alsi)
#     return response, magic_from_alsi, magic



#     # TODO: Second Call
#
#     try:
#
#         hash = hashlib.md5()
#         hash.update("{}PJAC".format(seed).encode('utf-8'))
#         verification_magic = hash.hexdigest()
#
#         # generate PJAC md5 from seed and compare to magic_from_alsi from response
#         # if magic_from_alsi != verification_magic:
#         #     print("verification of magic string failed")
#         #     return False
#         # print("Magic string verification succeeded")
#
#
#         data = {
#             "name": options.kemp_id,
#             "password": options.password,
#             "order": options.order_id,
#             "access": options.acc,
#             "vlm": options.virtual,
#             "id": options.sn,
#             "lmvers": options.version,
#             "uuid": options.uuid,
#             "mtype": options.mtype, #
#             "sku": options.bsku,
#             "zclm" : options.zclm #
#
#         }
#
#         responseCookie = requests.post("{}/licserv.php/getlicensetypes/{}".format(options.host, magic), cookies=response.cookies, data=data)
#         cookie_from_alsi = responseCookie.text
#         #print(cookie_from_alsi)
#
#         if 'available' == 0:
#             print("verification Response is failed")
#             return False
#         print("response cookie verification succeeded\n\n")
#
#     #TODO: Task 3 Display List of licenses for firmware versions greater or equal to 7.2.36
#
#
#         print("--- List of available License Type---")
#         licenses = json.loads(cookie_from_alsi)
#         count = 1
#         while count <= len(licenses):
#             for licenseType in licenses['categories']:
#                 print("\n[" + licenseType['description'] + "]:")
#                 for k in licenseType['licenseTypes']:
#                     name = k['name']
#                     available = k['available']
#                     print("[" + str(count) + "] = " + str(name) + " | " + "Available: " + str(available))
#                     count += 1
#
#         count = 1
#         num = input("\nEnter license number: ")
#         option = int(num)
#         while count <= len(licenses):
#             for licenseType in licenses['categories']:
#                 for k in licenseType['licenseTypes']:
#                     name = k['name']
#                     available = k['available']
#                     if(option == count):
#                         print("[" + str(count) + "] = " + str(name) + " | " + "Available: " + str(available))
#                     count += 1
#
#         # licenses = json.loads(cookie_from_alsi)
#         # count = 1
#         # num = input("\nEnter license number: ")
#         # option = int(num)
#         # while count <= len(licenses):
#         #     for licenseType in licenses['categories']:
#         #         print("\n[" + licenseType['description'] + "]:")
#         #         for k in licenseType['licenseTypes']:
#         #             name = k['name']
#         #             available = k['available']
#         #             if (option == count):
#         #                 print("[" + str(count) + "] = " + str(name) + " | " + "Available: " + str(available))
#         #             count += 1
#
#
#     except Exception as e:
#        print("EXCEPTION THROWN")
#        print(e)
#        exit(1)











if __name__ == '__main__':
    main()
