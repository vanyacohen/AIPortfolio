//
//  ViewController.m
//  controller
//
//  Created by Vanya Cohen on 12/2/16.
//  Copyright © 2016 vanyacohen. All rights reserved.
//

#import "ViewController.h"

@interface ViewController ()

@property NSInputStream *inputStream;
@property NSOutputStream *outputStream;
@property CMMotionManager *motionManager;
@property UIView *throttleView;
@property NSTimer *controlTimer;
@property int throttle;
@property int pitch;
@property int roll;
@property int yaw;
@property bool controlEnabled;
@property UIActivityIndicatorView *activityView;

@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    self.view.backgroundColor = [UIColor greenColor];
    _throttleView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, self.view.frame.size.width, self.view.frame.size.height)];
    _throttleView.backgroundColor = [UIColor redColor];
    [self.view addSubview:_throttleView];
    
    _activityView = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleWhiteLarge];
    _activityView.center = self.view.center;
    [_activityView startAnimating];
    [self.view addSubview:_activityView];
    
    _throttle = 0;
    _pitch = 123;
    _roll = 123;
    _yaw = 124;
    
    [self startNetworkCommunication];
    [self startDeviceMotionUpdates];
    _controlTimer = [NSTimer scheduledTimerWithTimeInterval:0.5f target:self selector:@selector(sendControlValues:) userInfo: nil repeats: YES];
    _controlEnabled = YES;
}

- (BOOL)canBecomeFirstResponder {
    return YES;
}

- (void)viewDidAppear:(BOOL)animated {
    [self becomeFirstResponder];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

-(void)sendControlValues:(NSTimer *)timer {
    if (_controlEnabled) {
        [self sendMessage:[NSString stringWithFormat:@"t%i\np%i\nr%i\ny%i\n", _throttle, _pitch, _roll, _yaw]];
    }
}

// Touch down, change throttle
- (void)touchesBegan:(NSSet *)touches withEvent:(UIEvent *)event {
    [super touchesBegan:touches withEvent:event];
    CGPoint location  = [touches.anyObject locationInView:self.view];
    CGRect frame = _throttleView.frame;
    frame.origin.y = location.y;
    _throttleView.frame = frame;
    
    _throttle = 255 * ((self.view.frame.size.height - location.y) / self.view.frame.size.height);
}

// Touch moved, change throttle
- (void)touchesMoved:(NSSet *)touches withEvent:(UIEvent *)event {
    [super touchesMoved:touches withEvent:event];
    CGPoint location  = [touches.anyObject locationInView:self.view];
    CGRect frame = _throttleView.frame;
    frame.origin.y = location.y;
    _throttleView.frame = frame;
    
    _throttle = 255 * ((self.view.frame.size.height - location.y) / self.view.frame.size.height);
}

// Touch up
- (void)touchesEnded:(NSSet *)touches withEvent:(UIEvent *)event {
    [super touchesEnded:touches withEvent:event];
    
}

// Motion event, process for unlocking
- (void)motionEnded:(UIEventSubtype)motion withEvent:(UIEvent *)event {
    if (motion == UIEventSubtypeMotionShake) {
        _controlEnabled = NO;
        [self sendMessage:@"unlock\n"];
        [NSTimer scheduledTimerWithTimeInterval:2.0f repeats:NO block:^(NSTimer *timer) {
            _controlEnabled = YES;
        }];
    }
}

// Process the motion events and write them to the console
- (void)startDeviceMotionUpdates {
    _motionManager = [[CMMotionManager alloc] init];
    _motionManager.deviceMotionUpdateInterval = 0.5;
    [_motionManager startDeviceMotionUpdatesToQueue:[NSOperationQueue currentQueue] withHandler:
        ^(CMDeviceMotion *data, NSError *error) {
            _pitch = ((data.attitude.pitch + M_PI / 2.0f) / M_PI) * 255;
            _pitch = MAX(70, MIN(135, _pitch));
            _roll = ((data.attitude.roll + M_PI / 2.0f) / M_PI) * 255;
            _roll = MAX(100, MIN(125, _roll));
            _yaw = ((data.attitude.yaw + M_PI / 2.0f) / M_PI) * 255 - 3;
            _yaw = MAX(100, MIN(145, _yaw));
            NSLog(@"%@", [NSString stringWithFormat:@"%i %i %f", _pitch, _roll, data.attitude.yaw]);
        }];
}

// Initialize the network connection
- (void)startNetworkCommunication {
    CFStreamCreatePairWithSocketToHost(NULL, (CFStringRef)@"192.168.0.100", 5555, &readStream, &writeStream);
    
    _inputStream = (__bridge_transfer NSInputStream *)readStream;
    _outputStream = (__bridge_transfer NSOutputStream *)writeStream;
    [_inputStream setDelegate:self];
    [_outputStream setDelegate:self];
    [_inputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
    [_outputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
    [_inputStream open];
    [_outputStream open];
}

// Send data to the controller
- (void)sendMessage:(NSString *)message {
    NSData *data = [[NSData alloc] initWithData:[message dataUsingEncoding:NSASCIIStringEncoding]];
    [_outputStream write:[data bytes] maxLength:[data length]];
}

// Handle network events, once connected hide the loading indicator
- (void)stream:(NSStream *)aStream handleEvent:(NSStreamEvent)eventCode {
    switch (eventCode) {
        case NSStreamEventHasBytesAvailable:
            break;
        case NSStreamEventOpenCompleted:
            [_activityView stopAnimating];
            break;
        case NSStreamEventErrorOccurred:
            break;
        default:
            break;
    }
}

@end
