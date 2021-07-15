//timer4 will interrupt at 1Hz

void configure_timer4(void){
  cli();//stop interrupts

  //set timer4 interrupt at 1Hz
  TCCR4A = 0;// set entire TCCR1A register to 0
  TCCR4B = 0;// same for TCCR1B
  TCNT4  = 0;//initialize counter value to 0
  
  // set compare match register for 1 Hz increments
  // OCR4A = 15624/1;// = (16*10^6) / (1*1024) - 1 (must be <65536)
  // set compare match register for 10 Hz increments
  // OCR4A = 6249;// = (16*10^6) / (10*256) - 1 (must be <65536)
  // set compare match register for 100 Hz increments
  OCR4A = 624;// = (16*10^6) / (100*256) - 1 (must be <65536)
  // set compare match register for 500 Hz increments
  // OCR4A = 124;// = (16*10^6) / (500*256) - 1 (must be <65536)
  
  // turn on CTC mode
  TCCR4B |= (1 << WGM12);
  
  // Set CS12 and CS10 bits for 1024 prescaler
  // TCCR4B |= (1 << CS12) | (1 << CS10);  
  // Set CS12 for 256 prescaler
  TCCR4B |= (1 << CS12);    
  
  // enable timer compare interrupt
  TIMSK4 |= (1 << OCIE4A);

  sei();//allow interrupts
}

void setup(){
  Serial.begin(115200);
  // Serial.begin(460800);
  
  // configure_timer4();
}

unsigned long tms = 0;
unsigned long ptms = 0;
unsigned long ntms = 0;
unsigned long cnt = 0;
unsigned long pcnt = 0;

const static int adcx_ndata = 100;
int adc0_arr[adcx_ndata];
int adc1_arr[adcx_ndata];
int adc2_arr[adcx_ndata];
int adc3_arr[adcx_ndata];
int adc4_arr[adcx_ndata];
int adc5_arr[adcx_ndata];
int adc6_arr[adcx_ndata];
int adc7_arr[adcx_ndata];
int adc8_arr[adcx_ndata];
int adc9_arr[adcx_ndata];
int adc10_arr[adcx_ndata];
int adc11_arr[adcx_ndata];
int adc12_arr[adcx_ndata];
int adc13_arr[adcx_ndata];
int adc14_arr[adcx_ndata];
int adc15_arr[adcx_ndata];
const static int adcx_nchan = 16;
int adcx_varr[adcx_nchan];

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
   
ISR(TIMER4_COMPA_vect){
  tms = millis();
  cnt ++;
  
  int adc0 = analogRead(A0);
  int adc1 = analogRead(A1);
  int adc2 = analogRead(A2);
  int adc3 = analogRead(A3);
  int adc4 = analogRead(A4);
  int adc5 = analogRead(A5);
  int adc6 = analogRead(A6);
  int adc7 = analogRead(A7);
  int adc8 = analogRead(A8);
  int adc9 = analogRead(A9);
  int adc10 = analogRead(A10);
  int adc11 = analogRead(A11);    
  int adc12 = analogRead(A12);
  int adc13 = analogRead(A13);
  int adc14 = analogRead(A14);
  int adc15 = analogRead(A15);   
}

void save_data(int val, int arr[], int i){
  arr[i] = val;
}

double moving_average(int val, int arr[], int ndata){
  //int arr[] = adc0_arr;
  // int lastval = arr[ndata-1];
  int i = 0;
  
  // Shift array to the left and add val
  // [ 0, 1, 2, 3, 4, 5 ] => [ val, 0, 1, 2, 3, 4]
  for(i = ndata-1; i >= 1; i--){
    arr[i] = arr[i-1];
  }
  arr[0] = val;
   
  // take average
  double newavg = 0;
  for(i = 0; i < ndata; i++){
    newavg = newavg + (1.0/ndata)*(double)arr[i];
  }  

  return newavg;
}

double static_average(int arr[], int ndata){  
  double newavg = 0;
  int i;
  for(i = 0; i < ndata; i++){
    newavg = newavg + (double)arr[i]/ndata;
  }  
  return newavg;
}

int num_lows(int arr[], int ndata){  
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

void sense_and_send(void){    
  if(cnt == adcx_ndata){
//    for(int chan=0; chan < adcx_nchan; chan++){
//      adcx_varr[chan] = process_data(chan);
//    }  
    send_info();
//    send_data(adcx_nchan+1);  // Send all at once
    
    cnt = 0; 
  }
  
  send_data(cnt);
  
  int adc0 = analogRead(A0);
  int adc1 = analogRead(A1);
  int adc2 = analogRead(A2);
  int adc3 = analogRead(A3);
  int adc4 = analogRead(A4);
  int adc5 = analogRead(A5);
  int adc6 = analogRead(A6);
  int adc7 = analogRead(A7);
  int adc8 = analogRead(A8);
  int adc9 = analogRead(A9);
  int adc10 = analogRead(A10);
  int adc11 = analogRead(A11);    
  int adc12 = analogRead(A12);
  int adc13 = analogRead(A13);
  int adc14 = analogRead(A14);
  int adc15 = analogRead(A15);  
  
  save_data(adc0, adc0_arr, cnt);
  save_data(adc1, adc1_arr, cnt);
  save_data(adc2, adc2_arr, cnt);
  save_data(adc3, adc3_arr, cnt);
  save_data(adc4, adc4_arr, cnt);
  save_data(adc5, adc5_arr, cnt);
  save_data(adc6, adc6_arr, cnt);
  save_data(adc7, adc7_arr, cnt);
  save_data(adc8, adc8_arr, cnt);
  save_data(adc9, adc9_arr, cnt);
  save_data(adc10, adc10_arr, cnt);
  save_data(adc11, adc11_arr, cnt);
  save_data(adc12, adc12_arr, cnt);
  save_data(adc13, adc13_arr, cnt);
  save_data(adc14, adc14_arr, cnt);  
  save_data(adc15, adc15_arr, cnt);  
  
  //send_info(); 
  //Serial.println("");  
  //Serial.flush(); 
  
  cnt ++;
}

int process_data(int chan){  
    int *varr = get_adcx_arr(chan);  
    int res;
    if(chan < 8){
      res = num_lows(varr, adcx_ndata);
    }
    else{
      res = (int)static_average(varr, adcx_ndata);
    }   
    return res;
}

void send_data(int chan){  
  if(chan < adcx_nchan){    
    adcx_varr[chan] = process_data(chan);
    //Serial.print(",");
    Serial.print(adcx_varr[chan]);
    Serial.print(",");
  }
  if(chan == adcx_nchan){
    Serial.println(""); 
  }  
  // Send all at once
//  if(chan == adcx_nchan+1){
//    for(int chan = 0; chan < adcx_nchan; chan++){
//      Serial.print(adcx_varr[chan]);    
//      Serial.print(",");
//    }
//    Serial.println("");     
//  }
}

void send_info(void){
  Serial.print(cnt);
  Serial.print(","); 
  Serial.print(tms); //, 3);
  Serial.print(","); 
  Serial.print((double)tms/1000, 3); //, 3);
  Serial.print(",");
  Serial.print(millis()-tms); //, 3);
  Serial.print(": ");
  //Serial.println("");  
  //Serial.flush();  
}

// the loop routine runs over and over again forever:
void loop() { 
//  if (cnt == pcnt){
//    // just wait for next samples
//  }
//  else{
//    if (tms <= 20000){    
//      send_info();
//    }
//    if (cnt != pcnt + 1){
//      Serial.println("Errror: (cnt != pcnt + 1)");
//      while(1){}
//    }
//    pcnt = cnt;  
//    ptms = tms; 
//  }

  tms = millis();
  if( tms >= ntms ){
    if (tms <= 20000){    
      sense_and_send();
      int tmscnt = (tms % 1000)/10; // (19980 % 1000)/10 = 98
      if(tmscnt == cnt){
        send_info();
        Serial.println(", tmscnt");
        while(1){};
      }
    }        
    // ntms = ntms + 10;
    ntms = ntms + 10;
  }
}
