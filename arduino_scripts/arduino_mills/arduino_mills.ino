void setup(){
    Serial.begin(115200);
    // Serial.begin(460800);  
}

unsigned long time = 0;
unsigned long next_time = 0;
unsigned long sample_cnt = 0;

const static int num_samples = 100;
int adc0_arr[num_samples];
int adc1_arr[num_samples];
int adc2_arr[num_samples];
int adc3_arr[num_samples];
int adc4_arr[num_samples];
int adc5_arr[num_samples];
int adc6_arr[num_samples];
int adc7_arr[num_samples];
int adc8_arr[num_samples];
int adc9_arr[num_samples];
int adc10_arr[num_samples];
int adc11_arr[num_samples];
int adc12_arr[num_samples];
int adc13_arr[num_samples];
int adc14_arr[num_samples];
int adc15_arr[num_samples];
const static int num_channels = 16;
int adcx_varr[num_channels];
static const int analog_pins[] = { 
    A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15};

int* get_adcx_arr(int chan){
    if(chan == 0){return adc0_arr;}
    if(chan == 1){return adc1_arr;}
    if(chan == 2){return adc2_arr;}
    if(chan == 3){return adc3_arr;}
    if(chan == 4){return adc4_arr;}
    if(chan == 5){return adc5_arr;}
    if(chan == 6){return adc6_arr;}
    if(chan == 7){return adc7_arr;}
    if(chan == 8){return adc8_arr;}
    if(chan == 9){return adc9_arr;}
    if(chan == 10){return adc10_arr;}
    if(chan == 11){return adc11_arr;}
    if(chan == 12){return adc12_arr;}
    if(chan == 13){return adc13_arr;}
    if(chan == 14){return adc14_arr;}
    if(chan == 15){return adc15_arr;}
}

void save_data(int val, int i, int chan){
    int *adcx_arr = get_adcx_arr(chan);
    adcx_arr[i] = val;
}

double pd_static_average(int arr[], int ndata){  
    double newavg = 0;
    int i;
    for(i = 0; i < ndata; i++){
    newavg = newavg + (double)arr[i]/ndata;
    }  
    return newavg;
}

int pd_num_lows(int arr[], int ndata){  
    int numlows = 0;
    int val0 = 300;
    int i;
    int val;
    for(i = 0; i < ndata; i++){
        val = arr[i];
        if(val <= val0){
            numlows = numlows + 1;
        }
    }  
    return numlows;
}

int pd_num_risingedge(int arr[], int ndata){  
    int num_risingedge = 0;
    int valt = 300;
    int i;
    int val1;
    int val2;
    for(i = 1; i < ndata; i++){
        val1 = arr[i-1]; 
        val2 = arr[i];
        if(val1 <= valt && val2 > valt){
            num_risingedge = num_risingedge + 1;
        }
    }
    return num_risingedge;
}

void collect_data(void){   
    int adcx = 0;
    for(int chan = 0; chan < num_channels; chan++){ //or i <= 4
        adcx = analogRead(analog_pins[chan]);
        save_data(adcx, sample_cnt, chan);
    }
}

void scheduled_task(void){    
    if(sample_cnt == num_samples){
        send_header();
    //    for(int chan=0; chan < num_channels; chan++){
    //      adcx_varr[chan] = process_data(chan);
    //    }  
    //    send_data(num_channels+1);  // Send all at once

        sample_cnt = 0; 
    }

    // send data
    int chan = sample_cnt;
    int res = 0;
    if(chan < num_channels){    
        res = process_data(chan);
        Serial.print(res);
        Serial.print(",");
    }
    if(chan == num_channels){
        Serial.println(""); 
    }   

    collect_data();  
    sample_cnt ++;
}

int process_data(int chan){  
    int *varr = get_adcx_arr(chan);  
    int res;
    if(chan < 8){
        // res = pd_num_lows(varr, num_samples);
        res = pd_num_risingedge(varr, num_samples);
    }
    else{
        res = (int)pd_static_average(varr, num_samples);
    }   
    return res;
}

void send_header(void){
    Serial.print(sample_cnt);
    Serial.print(","); 
    Serial.print(time); //, 3);
    Serial.print(","); 
    Serial.print((double)time/1000, 3); //, 3);
    Serial.print(",");
    Serial.print(millis()-time); //, 3);
    Serial.print(":");
    //Serial.println("");  
    //Serial.flush();  
}

void loop() { 
    int dtms = 1000 / num_samples;  
    time = millis();
    if( time >= next_time ){
        scheduled_task();
        int tmscnt = (time % 1000)/10; // (19980 % 1000)/10 = 98 // 100, 75000
        if(tmscnt == sample_cnt){
            send_header();
            Serial.println("tmscnt");
            while(1){};
        }        
        // next_time = next_time + 100;
        next_time = next_time + 10;
    }
}
