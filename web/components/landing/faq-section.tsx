'use client'

import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from '@/components/ui/accordion'

export function FAQSection() {
    const faqs = [
        {
            q: "What does 'Free Access' mean?",
            a: "It gives you full access to Swing Lite for 3 days. You can see live signals, use the scanner, and experience the platform. No credit card required."
        },
        {
            q: "Can I upgrade or downgrade later?",
            a: "Yes. You can upgrade from Lite to Pro or downgrade at any time. Changes take effect at the start of the next billing cycle."
        },
        {
            q: "What happens after the 3-day trial?",
            a: "If you don't upgrade, your account reverts to a limited state where you can no longer see live signals. You will not be charged unless you choose to subscribe."
        },
        {
            q: "What is the difference between Lite and Pro?",
            a: "Lite is great for following signals on major tokens. Pro gives you the AI Advisor to ask questions ('Why did we enter here?'), 1H timeframe signals for faster entries, and deeper 90-day history."
        }
    ]

    return (
        <section className="mx-auto max-w-3xl mt-16 mb-24 px-4 scroll-mt-24" id="faq">
            <h2 className="text-3xl font-bold text-center text-white mb-12">Frequently Asked Questions</h2>
            <Accordion type="single" collapsible className="w-full">
                {faqs.map((faq, i) => (
                    <AccordionItem key={i} value={`item-${i}`} className="border-white/10">
                        <AccordionTrigger className="text-left text-base font-medium text-white/90 hover:text-emerald-400 hover:no-underline py-6">
                            {faq.q}
                        </AccordionTrigger>
                        <AccordionContent className="text-muted-foreground leading-relaxed text-base pb-6">
                            {faq.a}
                        </AccordionContent>
                    </AccordionItem>
                ))}
            </Accordion>
        </section>
    )
}
