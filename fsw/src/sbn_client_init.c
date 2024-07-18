/*
** GSC-18396-1, “Software Bus Network Client for External Process”
**
** Copyright © 2019 United States Government as represented by
** the Administrator of the National Aeronautics and Space Administration.
** No copyright is claimed in the United States under Title 17, U.S. Code.
** All Other Rights Reserved.
**
** Licensed under the NASA Open Source Agreement version 1.3
** See "NOSA GSC-18396-1.pdf"
*/

#include <pthread.h>

#include "sbn_client.h"
#include "sbn_client_minders.h"
#include "sbn_client_utils.h"

/* Start additional includes for hostname snippet */
#include<sys/socket.h>
#include<netdb.h>	//hostent
#include<arpa/inet.h>

/* End additional includes for hostname snippet */



extern int sbn_client_sockfd;
extern int sbn_client_cpuId;

pthread_t receive_thread_id;
pthread_t heart_thread_id;


int32 SBN_Client_Init(void)
{
    int32 status = SBN_CLIENT_NO_STATUS_SET;
    int heart_thread_status = 0;
    int receive_thread_status = 0;

    /* 
        DNS Resolution for FSW Container 
        Start hostname snippet from: https://stackoverflow.com/questions/38002016/problems-with-gethostbyname-c
    */
    struct hostent *he;
    struct in_addr **addr_list;
    int i;

    char Addr[OS_MAX_API_NAME];

    if ( (he = gethostbyname(SBN_CLIENT_IP_ADDR) ) != NULL) 
    {
        addr_list = (struct in_addr **) he->h_addr_list;
        for(i = 0; addr_list[i] != NULL; i++) 
        {
            //Return the first one;
            strcpy(&Addr, inet_ntoa(*addr_list[i]) );
            break;
        }
    }
    /* 
        End hostname snippet from: https://stackoverflow.com/questions/38002016/problems-with-gethostbyname-c
    */
    
    log_message("SBN_Client Connecting to %s, %d\n", Addr, SBN_CLIENT_PORT);
    
    sbn_client_sockfd = connect_to_server(Addr, SBN_CLIENT_PORT);
    sbn_client_cpuId = 2; /* TODO: hardcoded, but should be set by cFS SBN ??*/

    if (sbn_client_sockfd < 0)
    {
        log_message(
         "SBN_CLIENT: ERROR Failed to get sbn_client_sockfd, cannot continue.");
        status = SBN_CLIENT_BAD_SOCK_FD_EID;
    }
    else
    {
        CFE_SBN_Client_InitPipeTbl();

        /* heartbeat thread establishes live connection */
        heart_thread_status = pthread_create(&heart_thread_id, NULL, 
            SBN_Client_HeartbeatMinder, NULL);
            
        status = check_pthread_create_status(heart_thread_status, 
            SBN_CLIENT_HEART_THREAD_CREATE_EID);
        
        /* receive thread monitors for messages */
        if (status == SBN_CLIENT_SUCCESS)
        {    
            receive_thread_status = pthread_create(&receive_thread_id, NULL, 
            SBN_Client_ReceiveMinder, NULL);
        
            status = check_pthread_create_status(receive_thread_status, 
                SBN_CLIENT_RECEIVE_THREAD_CREATE_EID);
        }/* end if */ 
        
    }/* end if */ 
    
    if (status != SBN_CLIENT_SUCCESS)
    {
        log_message("SBN_Client_Init error %d\n", status);
    }/* end if */ 
    
    return status;
}/* end SBN_Client_Init */