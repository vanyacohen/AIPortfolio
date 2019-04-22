//
//  ViewController.h
//  controller
//
//  Created by Vanya Cohen on 12/2/16.
//  Copyright © 2016 vanyacohen. All rights reserved.
//

#import <UIKit/UIKit.h>
@import CoreMotion;

@interface ViewController : UIViewController <NSStreamDelegate>
{
    CFReadStreamRef readStream;
    CFWriteStreamRef writeStream;
}

@end

